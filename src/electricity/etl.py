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
from utils import AGG_RESPONDENTS, STATE_ABBREV, status_print


class TransformCounty:
    def transform(self, ba_points_df, coord_df, pop_inc_df):
        df = self._isolate_state_county(ba_points_df)
        df = self._map_state_abbrev(df)
        df = self._merge_fips_code(df, coord_df)
        pop_inc = self._impute_missing_pop_inc(pop_inc_df)
        pop_inc = self._pivot_pop_inc(pop_inc)
        pop_inc = self._rename_pop_inc_cols(pop_inc)
        pop_inc = self._fill_na_fix_dtypes_pop_inc(pop_inc)
        return df.merge(pop_inc, on="fips_code", how="left")

    def _isolate_state_county(self, df):
        df = df[["county_name", "state_name"]].drop_duplicates()
        df["county_name"] = df["county_name"].str.split("; ")
        df = df.explode("county_name").reset_index(drop=True)
        return df

    def _map_state_abbrev(self, df):
        df["state_abbrev"] = df["state_name"].map(
            lambda state: STATE_ABBREV.get(state, state)
        )
        return df

    def _merge_fips_code(self, df, fips_df):
        fips_df.columns = fips_df.columns.str.strip()
        fips_df["GEOID"] = fips_df["GEOID"].astype(str).str.zfill(5)
        fips_df = fips_df.rename(
            columns={
                "USPS": "state_abbrev",
                "GEOID": "fips_code",
                "NAME": "county_name",
            }
        )
        df = df.merge(fips_df, on=["state_abbrev", "county_name"], how="left")[
            ["county_name", "state_name", "state_abbrev", "fips_code"]
        ]
        return df

    def _impute_missing_pop_inc(self, df):
        ff = df.copy()
        ff["GeoFIPS"] = ff["GeoFIPS"].str.replace('"', "").str.strip()
        ff = ff[ff["GeoFIPS"] == "09001"]
        ff["2024"] = pd.to_numeric(ff["2024"], errors="coerce")
        years = [str(y) for y in range(2018, 2024)]
        ff[years] = ff[years].astype(int)

        def impute_2024(row):
            vals = row[years]
            geo_avg_growth = (vals.iloc[-1] / vals.iloc[0]) ** (1 / (len(vals) - 1)) - 1
            return vals.iloc[-1] * (1 + geo_avg_growth)

        income_row = ff[ff["LineCode"] == 1.0].iloc[0]
        pop_row = ff[ff["LineCode"] == 2.0].iloc[0]

        income_2024 = impute_2024(income_row)
        pop_2024 = impute_2024(pop_row)
        per_cap_2024 = income_2024 / pop_2024 * 1000

        ff.loc[ff["LineCode"] == 1.0, "2024"] = income_2024
        ff.loc[ff["LineCode"] == 2.0, "2024"] = pop_2024
        ff.loc[ff["LineCode"] == 3.0, "2024"] = per_cap_2024

        return pd.concat([df, ff], ignore_index=True)[
            ["GeoFIPS", "Description", "Unit", "2024"]
        ].dropna()

    def _pivot_pop_inc(self, df):
        df = df.pivot(
            index="GeoFIPS", columns="Description", values="2024"
        ).reset_index()
        df["GeoFIPS"] = df["GeoFIPS"].str.replace('"', "").str.strip()
        return df

    def _rename_pop_inc_cols(self, df):
        return df.rename(
            columns={
                "GeoFIPS": "fips_code",
                "Per capita personal income (dollars) 2/": "personal_income_per_capita",
                "Personal income (thousands of dollars) ": "personal_income_total",
                "Population (persons) 1/": "est_population_2024",
            }
        )

    def _fill_na_fix_dtypes_pop_inc(self, df):
        cols = [
            "personal_income_per_capita",
            "personal_income_total",
            "est_population_2024",
        ]

        df[cols] = df[cols].replace("(NA)", None)
        df = df.dropna().copy()
        df[cols] = df[cols].astype("int64")
        return df


class TransformBA:
    def transform(self, df):
        df = self._drop_duplicates(df)
        df = self._rename_cols(df)
        return df

    def _drop_duplicates(self, df):
        df = df[["respondent", "respondent-name"]].drop_duplicates()
        return df[~df["respondent-name"].isin(AGG_RESPONDENTS)]

    def _rename_cols(self, df):
        return df.rename(
            columns={"respondent": "ba_code", "respondent-name": "ba_name"}
        )


class TransformFuelType:
    def transform(self, df):
        df = self._drop_duplicates(df)
        df = self._rename_cols(df)
        return df

    def _drop_duplicates(self, df):
        return df[["fueltype", "type-name"]].drop_duplicates()

    def _rename_cols(self, df):
        return df.rename(
            columns={"fueltype": "fuel_type_code", "type-name": "fuel_type_name"}
        )


class TransformWeatherLoc:
    def transform(self, df):
        return self._drop_duplicates(df)

    def _drop_duplicates(self, df):
        return df[["latitude", "longitude"]].drop_duplicates()


@dataclass
class ETLPaths:
    plant_data_path: Path
    generator_data_path: Path
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
        eia = ExtractEIA()
        excel = ExtractExcel()
        csv = ExtractCSV()
        parq = ExtractParquet()
        weather = ExtractWeather()

        status_print("Extracting EIA API")
        demand_df = eia.extract_demand()
        generation_df = eia.extract_generation()
        status_print("Extracting EIA API", True)

        status_print("Extracting Excel")
        plant_df = excel.extract(self._paths.plant_data_path)
        generator_df = excel.extract(self._paths.generator_data_path)
        ba_df = excel.extract(self._paths.ba_data_path, skiprows=0)
        status_print("Extracting Excel", True)

        status_print("Extracting CSV")
        pop_df = csv.extract(self._paths.pop_data_path, encoding="latin-1")
        coord_df = csv.extract(
            self._paths.coord_data_path, encoding="utf-8", delimiter="\t"
        )
        pop_inc_df = csv.extract(
            self._paths.pop_inc_data_path, encoding="latin-1", low_memory=False
        )
        status_print("Extracting CSV", True)

        status_print("Extracting parquet")
        ba_county_df = parq.extract(self._paths.ba_county_data_path)
        status_print("Extracting parquet", True)

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
        status_print("Transforming tables", True)

        print(weather_loc_table.head())
