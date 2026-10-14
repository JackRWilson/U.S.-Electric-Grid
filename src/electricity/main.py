import os

from dynaconf import Dynaconf
from etl import ETLPaths, ETLProcessor
from sqlalchemy import create_engine
from pathlib import Path

os.chdir(os.path.dirname(__file__))


def run():

    paths = ETLPaths(
        plant_data_path=Path("../../data/2___Plant_Y2025.xlsx"),
        generator_data_path=Path("../../data/3_1_Generator_Y2025.xlsx"),
        income_data_path=Path("../../data/city-income-est.csv"),
        pop_data_path=Path("../../data/sub-est2025.csv"),
        ba_data_path=Path("../../data/Balancing_Authority_2025.xlsx"),
        coord_data_path=Path("../../data/2020_Gaz_counties_national.txt"),
        ba_county_data_path=Path(
            "../../data/out_eia861__yearly_balancing_authority_service_territory.parquet"
        ),
    )

    def build_engine():
        settings = Dynaconf(envvar_prefix="DB", load_dotenv=True, dotenv_override=True)
        return create_engine(settings.ENGINE_URL, echo=False)

    engine = build_engine()

    with engine.connect() as conn:
        processor = ETLProcessor(conn, paths)
        processor.process()

    engine.dispose()


if __name__ == "__main__":
    run()
