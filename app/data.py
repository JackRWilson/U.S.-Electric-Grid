import pandas as pd
from dynaconf import Dynaconf
from sqlalchemy import create_engine
from datetime import datetime, timedelta, UTC


def build_engine():
    settings = Dynaconf(envvar_prefix="DB", load_dotenv=True, dotenv_override=True)
    return create_engine(settings.ENGINE_URL, echo=False)


ENGINE = engine = build_engine()


def extract_data(qry):
    df = pd.read_sql(qry, ENGINE)
    return df


def render_latest_completion():
    sql = """
    select last_period
    from etl_watermark
    where source = 'etl'
    """
    df = pd.read_sql(sql, ENGINE)

    if df.empty:
        return "No completed runs yet"
    completed = df.iloc[0]["last_period"]
    if pd.isna(completed):
        return "No completed runs yet"

    formatted = (
        pd.to_datetime(completed, utc=True)
        .tz_convert("America/Chicago")
        .strftime("%b %d, %Y %I:%M %p")
    )
    return formatted


def get_next_run_time(tz="America/Chicago"):
    now = datetime.now(UTC)
    next_run = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)

    formatted = (
        pd.to_datetime(next_run, utc=True)
        .tz_convert("America/Chicago")
        .strftime("%b %d, %Y %I:%M %p")
    )
    return formatted
