import pandas as pd


class Loader:
    def __init__(self, conn):
        self._conn = conn

    def _insert(self, df, table_name):
        df.to_sql(table_name, self._conn, if_exists="append", index=False)
        self._conn.commit()

    def _read_ids(self, table_name, cols):
        sql_cols = (", ").join(cols)
        qry = f"select {sql_cols} from {table_name};"
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
        table_name = "county"
        self._insert(df, table_name)
        return self._read_ids(table_name, ["county_id", "fips_code"])


class LoadBa(Loader):
    def load(self, df):
        table_name = "balancing_authority"
        self._insert(df, table_name)
        return self._read_ids(table_name, ["ba_id", "ba_code"])


class LoadFuelType(Loader):
    def load(self, df):
        table_name = "fuel_type"
        self._insert(df, table_name)
        return self._read_ids(table_name, ["fuel_type_id", "fuel_type_code"])


class LoadWeatherLoc(Loader):
    def load(self, df):
        table_name = "weather_location"
        self._insert(df, table_name)
        return self._read_ids(
            table_name, ["weather_location_id", "latitude", "longitude"]
        )


class LoadWeather(Loader):
    def load(self, df, weather_loc_db):
        table_name = "weather"
        df = self._join_fk(df, id_table=weather_loc_db, on=["latitude", "longitude"])
        self._insert(df, table_name)


class LoadBAWeatherLoc(Loader):
    def load(self, df, ba_db, weather_loc_db):
        table_name = "ba_weather_location"
        df = self._join_fk(df, id_table=ba_db, on=["ba_code"])
        df = self._join_fk(df, id_table=weather_loc_db, on=["latitude", "longitude"])
        self._insert(df, table_name)


class LoadDemand(Loader):
    def load(self, df, ba_db):
        table_name = "electric_demand"
        df = self._join_fk(df, id_table=ba_db, on=["ba_code"])
        self._insert(df, table_name)


class LoadGeneration(Loader):
    def load(self, df, ba_db, fuel_type_db):
        table_name = "electric_generation"
        df = self._join_fk(df, id_table=ba_db, on=["ba_code"])
        df = self._join_fk(df, id_table=fuel_type_db, on=["fuel_type_code"])
        self._insert(df, table_name)


class LoadBACounty(Loader):
    def load(self, df, ba_db, county_db):
        table_name = "ba_county"
        df = self._join_fk(df, id_table=ba_db, on=["ba_code"])
        df = self._join_fk(df, id_table=county_db, on=["fips_code"])
        self._insert(df, table_name)
