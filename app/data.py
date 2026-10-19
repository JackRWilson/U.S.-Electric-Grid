import pandas as pd
from dynaconf import Dynaconf
from sqlalchemy import create_engine


def build_engine():
    settings = Dynaconf(envvar_prefix="DB", load_dotenv=True, dotenv_override=True)
    return create_engine(settings.ENGINE_URL, echo=False)


ENGINE = engine = build_engine()


def extract_data(qry):
    df = pd.read_sql(qry, ENGINE)
    return df
