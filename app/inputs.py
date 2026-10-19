from dash import dcc
from data import extract_data


# Data tab
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
        style={"width": "250px"},
    )


# BA tab
def ba_metric_dropdown():
    metrics = {
        "avg_demand_mwh": {"label": "Avg demand (MWh)", "fmt": ",.0f", "unit": " MWh"},
        "renewable_pct": {"label": "Renewable %", "fmt": ".1f", "unit": "%"},
        "net_interchange_mwh": {
            "label": "Net interchange (MWh)",
            "fmt": ",.0f",
            "unit": " MWh",
        },
    }
    return dcc.Dropdown(
        [{"label": v["label"], "value": name} for name, v in metrics.items()],
        id="input-ba-metric-dropdown",
        value="avg_demand_mwh",
        clearable=False,
        style={"width": "250px"},
    )
