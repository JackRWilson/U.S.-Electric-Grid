import logging
import os
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd
from extract import *
from load import *
from transform import *
from watermark import ETLWatermark

OVERLAP = timedelta(hours=20)
logger = logging.getLogger(__name__)


@dataclass
class ETLPaths:
    plant_data_path: Path
    pop_data_path: Path
    ba_data_path: Path
    coord_data_path: Path
    ba_county_data_path: Path
    pop_inc_data_path: Path


class ETLProcessor:
    def __init__(self, conn, paths):
        self._conn = conn
        self._paths = paths
        self._watermark = ETLWatermark(conn)

    def _get_start_date(self, env_name):
        value = os.environ.get(env_name)

        if not value:
            return datetime.now(UTC).replace(tzinfo=None) - timedelta(days=90)

        try:
            return datetime.fromisoformat(value).replace(tzinfo=None)
        except ValueError as exc:
            raise ValueError(
                f"{env_name} must be an ISO date or datetime (e.g. 2026-07-17)."
            ) from exc

    def _is_first_run(self):
        sql = """
        select 1
        from electricity.etl_watermark
        where source = 'static'
        """
        return pd.read_sql(sql, self._conn).empty

    def _get_extract_start(self, source, default_start):
        watermark = self._watermark.extract(source)
        if watermark is None:
            return default_start
        return watermark - OVERLAP

    def _extract_eia(self):
        default_start = self._get_start_date("EIA_INITIAL_START")
        demand_start = self._get_extract_start("demand", default_start)
        generation_start = self._get_extract_start("generation", default_start)

        eia = ExtractEIA()
        demand_df = eia.extract_demand(start=demand_start)
        generation_df = eia.extract_generation(start=generation_start)

        demand_df = demand_df[demand_df["period"] >= demand_start]
        generation_df = generation_df[generation_df["period"] >= generation_start]

        return demand_df, generation_df

    def _extract_local_files(self):
        excel = ExtractExcel()
        csv = ExtractCSV()
        parq = ExtractParquet()
        return (
            excel.extract(self._paths.plant_data_path),
            excel.extract(self._paths.ba_data_path, skiprows=0),
            csv.extract(self._paths.pop_data_path, encoding="latin-1"),
            csv.extract(self._paths.coord_data_path, encoding="utf-8", delimiter="\t"),
            csv.extract(
                self._paths.pop_inc_data_path, encoding="latin-1", low_memory=False
            ),
            parq.extract(self._paths.ba_county_data_path),
        )

    def _extract_weather_loc(self):
        sql = """
        select
            weather_location_id,
            latitude,
            longitude
        from electricity.weather_location
        """
        return pd.read_sql(sql, self._conn)

    def _transform_demand(self, demand_df):
        if demand_df.empty:
            return pd.DataFrame(
                columns=[
                    "period",
                    "ba_code",
                    "demand_mwh",
                    "net_generation_mwh",
                    "total_interchange_mwh",
                ]
            )
        return TransformDemand().transform(demand_df)

    def _etl_dimensions_first_run(self, demand_df, generation_df):
        plant_df, ba_df, pop_df, coord_df, pop_inc_df, ba_county_df = (
            self._extract_local_files()
        )

        locations = BALocations(
            demand_df, ba_df, coord_df, ba_county_df, plant_df, pop_df
        )
        ba_points_df, coordinates_df = locations.get_coords()

        county_table = TransformCounty().transform(ba_points_df, coord_df, pop_inc_df)
        ba_table = TransformBA().transform(demand_df, ba_df)
        fuel_type_table = TransformFuelType().transform(generation_df)
        weather_loc_table = TransformWeatherLoc().transform(ba_points_df)
        ba_weather_loc_table = TransformBAWeatherLoc().transform(ba_points_df)
        ba_county_table = TransformBACounty().transform(ba_points_df, coord_df)

        county_db = LoadCounties(self._conn).load(county_table)
        ba_db = LoadBa(self._conn).load(ba_table)
        fuel_type_db = LoadFuelType(self._conn).load(fuel_type_table)
        weather_loc_db = LoadWeatherLoc(self._conn).load(weather_loc_table)
        LoadBAWeatherLoc(self._conn).load(ba_weather_loc_table, ba_db, weather_loc_db)
        LoadBACounty(self._conn).load(ba_county_table, ba_db, county_db)

        return ba_db, fuel_type_db, weather_loc_db

    def _etl_dimensions_later_run(self, demand_df, generation_df):
        empty_ba_names = pd.DataFrame(columns=["BA Code", "Balancing Authority Name"])
        ba_table = TransformBA().transform(demand_df, empty_ba_names)
        fuel_type_table = TransformFuelType().transform(generation_df)

        ba_db = LoadBa(self._conn).load(ba_table, update_existing=False)
        fuel_type_db = LoadFuelType(self._conn).load(
            fuel_type_table, update_existing=False
        )
        weather_loc_db = self._extract_weather_loc()

        return ba_db, fuel_type_db, weather_loc_db

    def _etl_weather(self, weather_loc_db):
        if weather_loc_db.empty:
            return pd.DataFrame()

        weather_start = self._get_extract_start(
            "weather", self._get_start_date("WEATHER_INITIAL_START")
        )
        logger.info(
            "Starting Open-Meteo weather extraction for %d locations from %s",
            len(weather_loc_db[["latitude", "longitude"]].drop_duplicates()),
            weather_start,
        )
        coordinates_df = weather_loc_db[["latitude", "longitude"]].drop_duplicates()
        weather_df = ExtractWeather().extract_weather(
            coordinates_df, start=weather_start
        )
        weather_df = weather_df[weather_df["time"] >= weather_start]

        weather_table = TransformWeather().transform(weather_df)
        LoadWeather(self._conn).load(weather_table, weather_loc_db)

        return weather_table

    def process(self):
        logger.info("ETL started")
        self._watermark.ensure_table()
        is_first_run = self._is_first_run()
        logger.info("First Run: %s", is_first_run)

        demand_df, generation_df = self._extract_eia()
        logger.info(
            "Extracted EIA: %d demand rows, %d generation rows",
            len(demand_df),
            len(generation_df),
        )

        if is_first_run:
            ba_db, fuel_type_db, weather_loc_db = self._etl_dimensions_first_run(
                demand_df, generation_df
            )
        else:
            ba_db, fuel_type_db, weather_loc_db = self._etl_dimensions_later_run(
                demand_df, generation_df
            )
        logger.info("Loaded dimensions")

        demand_table = self._transform_demand(demand_df)
        generation_table = TransformGeneration().transform(generation_df)
        LoadDemand(self._conn).load(demand_table, ba_db)
        LoadGeneration(self._conn).load(generation_table, ba_db, fuel_type_db)
        logger.info("Loaded demand and generation")

        weather_table = self._etl_weather(weather_loc_db)
        logger.info("Loaded weather: %d rows", len(weather_table))

        self._watermark.load_max_period("demand", demand_table, "period")
        self._watermark.load_max_period("generation", generation_table, "period")
        self._watermark.load_max_period("weather", weather_table, "period")
        if is_first_run:
            self._watermark.load("static", None)

        logger.info("ETL complete")
