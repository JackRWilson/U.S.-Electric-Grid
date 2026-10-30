import sys
from pathlib import Path

import pendulum
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.sdk import dag, task

ELECTRICITY_SRC = Path("/opt/airflow/src/electricity")
DATA_DIR = Path("/opt/airflow/data")
sys.path.insert(0, str(ELECTRICITY_SRC))

from etl import ETLPaths, ETLProcessor


@dag(
    schedule="0 * * * *",
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    max_active_runs=1,
    template_searchpath=["/opt/airflow/db"],
    tags=["electricity", "etl"],
)
def electricity_etl_dag():
    electricity_schema = SQLExecuteQueryOperator(
        task_id="electricity_schema",
        sql="electricity_schema.sql",
        conn_id="electricity_pg",
    )

    @task()
    def run_electricity_etl():
        paths = ETLPaths(
            plant_data_path=DATA_DIR / "2___Plant_Y2025.xlsx",
            pop_data_path=DATA_DIR / "sub-est2025.csv",
            ba_data_path=DATA_DIR / "Balancing_Authority_2025.xlsx",
            coord_data_path=DATA_DIR / "2020_Gaz_counties_national.txt",
            ba_county_data_path=DATA_DIR
            / "out_eia861__yearly_balancing_authority_service_territory.parquet",
            pop_inc_data_path=DATA_DIR / "CAINC1__ALL_AREAS_1969_2024.csv",
        )
        hook = PostgresHook(postgres_conn_id="electricity_pg")
        engine = hook.get_sqlalchemy_engine()
        try:
            with engine.begin() as conn:
                ETLProcessor(conn, paths).process()
        finally:
            engine.dispose()

    electricity_schema >> run_electricity_etl()


electricity_etl_dag()
