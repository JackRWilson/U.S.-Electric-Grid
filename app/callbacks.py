import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback
from plotly.subplots import make_subplots
import pandas as pd

from data import extract_data


# Data tab - KPIs
@callback(
    Output("output-data-kpi-date-range", "children"),
    Output("output-data-kpi-total-mwh", "children"),
    Input("input-data-ba-dropdown", "value"),
)
def update_demand_kpis(selected_ba):
    ba_filter = f"where ba.ba_code = '{selected_ba}'" if selected_ba else ""

    sql = f"""
    select
        min(d.period) as first_period,
        max(d.period) as last_period,
        sum(d.demand_mwh) as total_mwh
    from electric_demand d
    inner join balancing_authority ba on ba.ba_id = d.ba_id
    {ba_filter}
    """
    df = extract_data(sql)

    row = df.iloc[0]
    if pd.isna(row["first_period"]):
        return "No data", "No data"

    first = pd.to_datetime(row["first_period"]).strftime("%b %d, %Y")
    last = pd.to_datetime(row["last_period"]).strftime("%b %d, %Y")
    total_mwh = float(row["total_mwh"])
    total_label = f"{total_mwh:,.0f} MWh"

    return f"{first} - {last}", total_label


# Data tab - Demand / Temp graph
@callback(
    Output(component_id="output-demand-time-line-graph", component_property="figure"),
    Input(component_id="input-data-ba-dropdown", component_property="value"),
)
def update_demand_time_line_graph(selected_ba):
    ba_filter = f"where ba.ba_code = '{selected_ba}'" if selected_ba else ""

    sql = f"""
    with demand as (
        select
            d.period,
            avg(d.demand_mwh) as demand_mwh
        from electric_demand d
        inner join balancing_authority ba on ba.ba_id = d.ba_id
        {ba_filter}
        group by d.period
    ),
    temp as (
        select 
            w.period,
            sum(w.temp * bwl.weather_weight) / sum(bwl.weather_weight) as temp
        from weather w
        inner join ba_weather_location bwl on bwl.weather_location_id = w.weather_location_id
        inner join balancing_authority ba on ba.ba_id = bwl.ba_id
        {ba_filter}
        group by w.period
    )
    select 
        demand.period,
        demand.demand_mwh, 
        temp.temp
    from demand
    inner join temp on temp.period = demand.period
    order by demand.period
    """
    df = extract_data(sql)

    ba = selected_ba if selected_ba else "All BAs (average)"

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x=df["period"], y=df["demand_mwh"], name="Demand (MWh)"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=df["period"], y=df["temp"], name="Temperature (F)"),
        secondary_y=True,
    )

    fig.update_xaxes(title_text="Time")
    fig.update_yaxes(title_text="Demand (MWh)", secondary_y=False)
    fig.update_yaxes(title_text="Temperature (F)", secondary_y=True, showgrid=False)
    fig.update_layout(
        title=f"Demand & Temp Over Time - {ba}",
        hovermode="x unified",
        legend={"orientation": "h", "y": 1.1},
    )
    return fig
