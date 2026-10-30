from dash import dcc
from styles import DROPDOWN_STYLE
from tables import DATA_TABLES

from data import extract_data


# Data tab - BA dropdown
def data_ba_dropdown():
    sql = """
    select distinct ba_code 
    from balancing_authority 
    order by ba_code
    """
    df = extract_data(sql)
    return dcc.Dropdown(
        [{"label": name, "value": name} for name in df["ba_code"].unique()],
        id="input-data-ba-dropdown",
        multi=False,
        placeholder="All BAs",
        style={**DROPDOWN_STYLE, "width": "100%"},
    )


# Data tab - Table dropdown
def data_table_dropdown():
    return dcc.Dropdown(
        [
            {"label": config["table"], "value": key}
            for key, config in DATA_TABLES.items()
        ],
        id="input-data-table-dropdown",
        value=next(iter(DATA_TABLES)),
        clearable=False,
        searchable=True,
        style={
            **DROPDOWN_STYLE,
            "width": "100%",
        },
    )


# BA tab
def ba_metric_dropdown():
    metrics = {
        "avg_demand_mwh": {
            "label": "Avg Demand (MWh)",
            "fmt": ",.0f",
            "unit": " MWh",
        },
        "demand_index": {
            "label": "Peak-to-Avg Demand",
            "fmt": ".2f",
            "unit": "x",
        },
        "avg_generation_mwh": {
            "label": "Avg Generation (MWh)",
            "fmt": ",.0f",
            "unit": " MWh",
        },
        "renewable_pct": {
            "label": "Renewable Generation (%)",
            "fmt": ".1f",
            "unit": "%",
        },
        "net_interchange_pct": {
            "label": "Net Interchange (% of Demand)",
            "fmt": ".1f",
            "unit": "%",
        },
    }
    return dcc.Dropdown(
        [{"label": v["label"], "value": name} for name, v in metrics.items()],
        id="input-ba-metric-dropdown",
        value="avg_demand_mwh",
        clearable=False,
        style={**DROPDOWN_STYLE, "width": "100%"},
    )


# Weather tab
def weather_ba_dropdown():
    sql = """
    select distinct ba_code 
    from electric_demand d
    inner join balancing_authority ba on ba.ba_id = d.ba_id
    union
    select distinct ba_code 
    from electric_generation g
    inner join balancing_authority ba on ba.ba_id = g.ba_id
    order by ba_code
    """
    df = extract_data(sql)
    return dcc.Dropdown(
        [{"label": name, "value": name} for name in df["ba_code"].unique()],
        id="input-weather-ba-dropdown",
        multi=False,
        placeholder="All BAs",
        style={**DROPDOWN_STYLE, "width": "100%"},
    )
