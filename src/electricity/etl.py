from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from extract import (
    BALocations,
    ExtractCSV,
    ExtractEIA,
    ExtractExcel,
    ExtractParquet,
    ExtractWeather,
)


class Transform:
    pass


@dataclass
class ETLPaths:
    plant_data_path: Path
    generator_data_path: Path
    income_data_path: Path
    pop_data_path: Path
    ba_data_path: Path
    coord_data_path: Path
    ba_county_data_path: Path


class ETLProcessor:
    def __init__(self, conn, paths):
        self._conn = conn
        self._paths = paths

    def process(self):
        print("Extracting...")
        eia = ExtractEIA()
        excel = ExtractExcel()
        csv = ExtractCSV()
        parq = ExtractParquet()
        weather = ExtractWeather()

        demand_df = eia.extract_demand()
        generation_df = eia.extract_generation()

        plant_df = excel.extract(self._paths.plant_data_path)
        generator_df = excel.extract(self._paths.generator_data_path)
        ba_df = excel.extract(self._paths.ba_data_path, skiprows=0)

        income_df = csv.extract(self._paths.income_data_path)
        pop_df = csv.extract(self._paths.pop_data_path, encoding="latin-1")
        coord_df = csv.extract(
            self._paths.coord_data_path, encoding="latin-1", delimiter="\t"
        )

        ba_county_df = parq.extract(self._paths.ba_county_data_path)

        locations = BALocations(
            demand_df, ba_df, coord_df, ba_county_df, plant_df, pop_df
        )
        ba_points_df, coordinates_df = locations.get_coords()
        ba_points_df.to_csv("ba_points.csv", index=False)
        weather_df = weather.extract_weather(coordinates_df)
