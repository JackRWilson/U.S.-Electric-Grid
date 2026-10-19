from dash import dcc
from data import extract_data

# Data tab
def data_ba_dropdown():
    df = extract_data("select distinct ba_code from balancing_authority order by ba_code")
    return dcc.Dropdown(
        [
            {"label": name, "value": name}
            for name in df["ba_code"].unique()
        ],
        id="input-data-ba-dropdown",
        multi=False,
        placeholder="All BAs",
        style={"width": "250px"},
    )