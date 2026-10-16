import pandas as pd
from utils import AGG_RESPONDENTS, STATE_ABBREV, WEATHER_CODES


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
        df["state_abbrev"] = df["state_name"].map(STATE_ABBREV)
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


class TransformWeather:
    def transform(self, df):
        df = self._map_weather_codes(df)
        df = self._rename_cols(df)
        return df

    def _map_weather_codes(self, df):
        df["weather_code"] = df["weather_code"].map(WEATHER_CODES)
        return df

    def _rename_cols(self, df):
        return df.rename(
            columns={
                "time": "period",
                "temperature_2m": "temp",
                "cloud_cover": "total_cloud_cover",
            }
        )


class TransformDemand:
    def transform(self, df):
        df = self._pivot_metrics(df)
        df = self._impute_missing_values(df)
        df = self._rename_cols(df)
        df = self._convert_dtypes(df)
        return df

    def _pivot_metrics(self, df):
        df = df[["period", "respondent", "type-name", "value"]]
        df = df.pivot(
            index=["period", "respondent"], columns="type-name", values="value"
        ).reset_index()
        return df

    def _impute_missing_values(self, df):
        condition = (df["Net generation"] == df["Total interchange"]) & (
            df["Demand"].isna()
        )
        df.loc[condition, "Demand"] = 0

        condition = (df["Demand"] == df["Total interchange"]) & (
            df["Net generation"].isna()
        )
        df.loc[condition, "Net generation"] = 0

        condition = (
            df["Net generation"].notna()
            & df["Total interchange"].notna()
            & df["Demand"].isna()
        )
        df.loc[condition, "Demand"] = (
            df.loc[condition, "Net generation"] - df.loc[condition, "Total interchange"]
        )

        condition = (
            df["Net generation"].isna()
            & df["Total interchange"].notna()
            & df["Demand"].notna()
        )
        df.loc[condition, "Net generation"] = (
            df.loc[condition, "Demand"] + df.loc[condition, "Total interchange"]
        )

        condition = (
            df["Net generation"].notna()
            & df["Total interchange"].isna()
            & df["Demand"].notna()
        )
        df.loc[condition, "Total interchange"] = (
            df.loc[condition, "Demand"] - df.loc[condition, "Net generation"]
        )
        return df

    def _rename_cols(self, df):
        df = df.rename(
            columns={
                "Demand": "demand_mwh",
                "Net generation": "net_generation_mwh",
                "Total interchange": "total_interchange_mwh",
                "respondent": "ba_code",
            }
        )
        df.columns.name = None
        return df

    def _convert_dtypes(self, df):
        cols = ["demand_mwh", "net_generation_mwh", "total_interchange_mwh"]
        for col in cols:
            df[col] = df[col].astype("Int64")
        return df


class TransformBAWeatherLoc:
    def transform(self, df):
        return self._rename_filter_cols(df)

    def _rename_filter_cols(self, df):
        df = df[["respondent", "latitude", "longitude", "weather_weight"]]
        df = df.rename(columns={"respondent": "ba_code"})
        return df


class TransformBACounty:
    def transform(self, ba_points_df, coord_df):
        df = self._map_state_abbrev(ba_points_df)
        df = self._isolate_state_county(df)
        df = self._merge_fips_code(df, coord_df)
        return df

    def _map_state_abbrev(self, df):
        df["state_abbrev"] = df["state_name"].map(STATE_ABBREV)
        df = df[["respondent", "county_name", "state_abbrev"]]
        return df

    def _isolate_state_county(self, df):
        df["county_name"] = df["county_name"].str.split("; ")
        df = df.explode("county_name").reset_index(drop=True)
        return df

    def _merge_fips_code(self, df, fips_df):
        fips_df.columns = fips_df.columns.str.strip()
        fips_df["GEOID"] = fips_df["GEOID"].astype(str).str.zfill(5)
        fips_df = fips_df[["USPS", "NAME", "GEOID"]]
        fips_df = fips_df.rename(
            columns={
                "USPS": "state_abbrev",
                "GEOID": "fips_code",
                "NAME": "county_name",
            }
        )
        df = df.merge(fips_df, on=["state_abbrev", "county_name"], how="left")[
            ["respondent", "fips_code"]
        ].rename(columns={"respondent": "ba_code"})

        return df


class TransformGeneration:
    def transform(self, df):
        return self._rename_cols(df)

    def _rename_cols(self, df):
        return df[["period", "respondent", "fueltype", "value"]].rename(
            columns={
                "respondent": "ba_code",
                "fueltype": "fuel_type_code",
                "value": "generation_mwh",
            }
        )