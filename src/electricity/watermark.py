import pandas as pd
from sqlalchemy import text


class ETLWatermark:
    def __init__(self, conn):
        self._conn = conn

    def ensure_table(self):
        sql = """
        create schema if not exists electricity
        """
        self._conn.execute(text(sql))

        sql = """
        create table if not exists electricity.etl_watermark (
            source varchar(50) primary key,
            last_period timestamp
        )
        """
        self._conn.execute(text(sql))

    def extract(self, source):
        sql = """
        select last_period
        from electricity.etl_watermark
        where source = :source
        """
        df = pd.read_sql(text(sql), self._conn, params={"source": source})
        if df.empty:
            return None
        return df["last_period"].iloc[0]

    def load(self, source, period):
        sql = """
        insert into electricity.etl_watermark
            (source, last_period)
            values (:source, :period)
        on conflict (source)
        do update set last_period = excluded.last_period
        """
        self._conn.execute(text(sql), {"source": source, "period": period})

    def load_max_period(self, source, df, col):
        if df.empty:
            return
        newest = pd.to_datetime(df[col].max())
        newest = newest.to_pydatetime()
        if pd.notna(newest):
            self.load(source, newest)
