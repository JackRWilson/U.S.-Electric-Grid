from datetime import UTC, datetime, timedelta

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


def get_natural_gas_share(fuel_figure):
    fuel_names = list(fuel_figure.data[0].x)
    fuel_values = [float(value) for value in fuel_figure.data[0].y]

    total_generation = sum(fuel_values)
    if total_generation <= 0:
        return "N/A"

    natural_gas_generation = 0.0
    for fuel_name, fuel_value in zip(fuel_names, fuel_values):
        if fuel_name == "Natural Gas":
            natural_gas_generation += fuel_value

    natural_gas_share = natural_gas_generation / total_generation
    return f"{natural_gas_share:.0%}"


def get_temp_balance_point(weather_kpi_values):
    balance_temp_text = weather_kpi_values[1]
    balance_demand_text = weather_kpi_values[2].removesuffix(" Average")
    return balance_temp_text, balance_demand_text


def get_temp_balance_number(balance_temp_text):
    if not balance_temp_text.endswith("°F"):
        return None
    return float(balance_temp_text.removesuffix("°F"))


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


def get_next_run_time():
    now = datetime.now(UTC)
    next_run = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)

    formatted = (
        pd.to_datetime(next_run, utc=True)
        .tz_convert("America/Chicago")
        .strftime("%b %d, %Y %I:%M %p")
    )
    return formatted
