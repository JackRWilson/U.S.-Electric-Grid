import pandas as pd
from sqlalchemy import MetaData, Table
from sqlalchemy.dialects.postgresql import insert


class Loader:
    def __init__(self, conn):
        self._conn = conn

    def _upsert(self, df, table_name, conflict_cols, update_cols=None):
        if df.empty:
            return

        df = df.drop_duplicates(subset=conflict_cols, keep="last")
        values = (
            df.astype(object)
            .where(pd.notna(df), None)
            .to_dict(orient="records")
        )
        table = Table(
            table_name.rsplit(".", maxsplit=1)[-1],
            MetaData(),
            schema="electricity",
            autoload_with=self._conn,
        )
        for offset in range(0, len(values), 1000):
            batch = values[offset : offset + 1000]
            statement = insert(table).values(batch)
            if update_cols:
                statement = statement.on_conflict_do_update(
                    index_elements=conflict_cols,
                    set_={col: getattr(statement.excluded, col) for col in update_cols},
                )
            else:
                statement = statement.on_conflict_do_nothing(
                    index_elements=conflict_cols
                )
            self._conn.execute(statement)

    def _read_ids(self, table_name, cols):
        sql_cols = (", ").join(cols)
        qry = f"select {sql_cols} from electricity.{table_name};"
        return pd.read_sql(qry, self._conn)

    def _join_fk(self, df, id_table, on: list):
        merged_df = df.merge(id_table, on=on, how="left")
        for col in id_table.columns:
            if "id" in col:
                id_col = col
        missing = merged_df[id_col].isna().sum()
        if missing > 0:
            raise ValueError(
                f"{missing} rows in {on} failed to match with a foreign key."
            )
        return merged_df.drop(columns=[col for col in on])


class LoadCounties(Loader):
    def load(self, df):
        self._upsert(
            df,
            "electricity.county",
            ["fips_code"],
            [
                "state_abbrev",
                "state_name",
                "county_name",
                "est_population_2024",
                "personal_income_total",
                "personal_income_per_capita",
            ],
        )
        table_name = "county"
        return self._read_ids(table_name, ["county_id", "fips_code"])


class LoadBa(Loader):
    def load(self, df, update_existing=True):
        table_name = "balancing_authority"
        update_cols = ["ba_name"] if update_existing else None
        self._upsert(
            df,
            f"electricity.{table_name}",
            ["ba_code"],
            update_cols,
        )
        return self._read_ids(table_name, ["ba_id", "ba_code"])


class LoadFuelType(Loader):
    def load(self, df, update_existing=True):
        table_name = "fuel_type"
        update_cols = ["fuel_type_name"] if update_existing else None
        self._upsert(
            df,
            f"electricity.{table_name}",
            ["fuel_type_code"],
            update_cols,
        )
        return self._read_ids(table_name, ["fuel_type_id", "fuel_type_code"])


class LoadWeatherLoc(Loader):
    def load(self, df):
        table_name = "weather_location"
        self._upsert(
            df,
            f"electricity.{table_name}",
            ["latitude", "longitude"],
        )
        return self._read_ids(
            table_name, ["weather_location_id", "latitude", "longitude"]
        )


class LoadWeather(Loader):
    def load(self, df, weather_loc_db):
        table_name = "weather"
        df = self._join_fk(df, id_table=weather_loc_db, on=["latitude", "longitude"])
        self._upsert(
            df,
            f"electricity.{table_name}",
            ["weather_location_id", "period"],
            [
                "temp",
                "precipitation",
                "rain",
                "showers",
                "snowfall",
                "total_cloud_cover",
                "weather_code",
                "wind_speed_10m",
                "wind_speed_80m",
                "wind_speed_120m",
                "wind_speed_180m",
                "wind_gusts_10m",
            ],
        )


class LoadBAWeatherLoc(Loader):
    def load(self, df, ba_db, weather_loc_db):
        table_name = "ba_weather_location"
        df = self._join_fk(df, id_table=ba_db, on=["ba_code"])
        df = self._join_fk(df, id_table=weather_loc_db, on=["latitude", "longitude"])
        self._upsert(
            df,
            f"electricity.{table_name}",
            ["ba_id", "weather_location_id"],
            ["weather_weight"],
        )


class LoadDemand(Loader):
    def load(self, df, ba_db):
        table_name = "electric_demand"
        df = self._join_fk(df, id_table=ba_db, on=["ba_code"])
        self._upsert(
            df,
            f"electricity.{table_name}",
            ["ba_id", "period"],
            ["demand_mwh", "net_generation_mwh", "total_interchange_mwh"],
        )


class LoadGeneration(Loader):
    def load(self, df, ba_db, fuel_type_db):
        table_name = "electric_generation"
        df = self._join_fk(df, id_table=ba_db, on=["ba_code"])
        df = self._join_fk(df, id_table=fuel_type_db, on=["fuel_type_code"])
        self._upsert(
            df,
            f"electricity.{table_name}",
            ["ba_id", "period", "fuel_type_id"],
            ["generation_mwh"],
        )


class LoadBACounty(Loader):
    def load(self, df, ba_db, county_db):
        table_name = "ba_county"
        df = self._join_fk(df, id_table=ba_db, on=["ba_code"])
        df = self._join_fk(df, id_table=county_db, on=["fips_code"])
        self._upsert(
            df,
            f"electricity.{table_name}",
            ["ba_id", "county_id"],
        )
