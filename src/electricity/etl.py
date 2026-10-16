from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from extract import *
from transform import *
from utils import status_print


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

    def process(self):
        print("Starting ETL...")
        eia = ExtractEIA()
        excel = ExtractExcel()
        csv = ExtractCSV()
        parq = ExtractParquet()
        weather = ExtractWeather()

        status_print("Extracting EIA API")
        demand_df = eia.extract_demand()
        generation_df = eia.extract_generation()
        status_print("Extracting EIA API", True)

        status_print("Extracting local files")
        plant_df = excel.extract(self._paths.plant_data_path)
        ba_df = excel.extract(self._paths.ba_data_path, skiprows=0)
        pop_df = csv.extract(self._paths.pop_data_path, encoding="latin-1")
        coord_df = csv.extract(
            self._paths.coord_data_path, encoding="utf-8", delimiter="\t"
        )
        pop_inc_df = csv.extract(
            self._paths.pop_inc_data_path, encoding="latin-1", low_memory=False
        )
        ba_county_df = parq.extract(self._paths.ba_county_data_path)
        status_print("Extracting local files", True)

        status_print("Extracting weather API")
        locations = BALocations(
            demand_df, ba_df, coord_df, ba_county_df, plant_df, pop_df
        )
        ba_points_df, coordinates_df = locations.get_coords()
        weather_df = weather.extract_weather(coordinates_df)
        status_print("Extracting weather API", True)

        # --------------------------------------------------

        status_print("Transforming tables")
        county_table = TransformCounty().transform(ba_points_df, coord_df, pop_inc_df)
        ba_table = TransformBA().transform(demand_df)
        fuel_type_table = TransformFuelType().transform(generation_df)
        weather_loc_table = TransformWeatherLoc().transform(ba_points_df)
        weather_table = TransformWeather().transform(
            weather_df
        )  # Still needs weather_location_id on lat, long
        demand_table = TransformDemand().transform(
            demand_df
        )  # Still needs ba_id on ba_code
        ba_weather_loc_table = TransformBAWeatherLoc().transform(
            ba_points_df
        )  # Still needs ba_id on ba_code and weather_loc_id on lat, long
        ba_county_table = TransformBACounty().transform(
            ba_points_df, coord_df
        )  # Still needs ba_id on ba_code and county_id on fips_code
        generation_table = TransformGeneration().transform(
            generation_df
        )  # Still needs ba_id on ba_code and fuel_type_id on fuel_type_code
        status_print("Transforming tables", True)

        # --------------------------------------------------
        
        status_print("Loading tables")
        
        status_print("Loading tables", True)
        print("ETL Complete.")