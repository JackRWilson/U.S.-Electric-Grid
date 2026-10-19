import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback, html
from plotly.subplots import make_subplots

from data import extract_data


# Data tab - KPIs
@callback(
    Output(component_id="output-data-kpi-date-range", component_property="children"),
    Output(component_id="output-data-kpi-total-mwh", component_property="children"),
    Input(component_id="input-data-ba-dropdown", component_property="value"),
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
        go.Scatter(x=df["period"], y=df["temp"], name="Temperature (°F)"),
        secondary_y=True,
    )

    fig.update_xaxes(title_text="Time")
    fig.update_yaxes(title_text="Demand (MWh)", secondary_y=False)
    fig.update_yaxes(title_text="Temperature (°F)", secondary_y=True, showgrid=False)
    fig.update_layout(
        title=f"Demand & Temp Over Time - {ba}",
        hovermode="x unified",
        legend={"orientation": "h", "y": 1.1},
    )
    return fig


# BA tab - BA metrics
def load_ba_metrics():
    sql = """
    with demand as (
        select
            ba_id,
            avg(demand_mwh) as avg_demand_mwh,
            avg(total_interchange_mwh) as net_interchange_mwh
        from electric_demand
        group by ba_id
    ),
    generation as (
        select
            g.ba_id,
            avg(g.generation_mwh) as avg_generation_mwh,
            100.0 * sum(case when ft.fuel_type_code in ('WAT', 'SUN', 'WND') then g.generation_mwh else 0 end)
                / nullif(sum(g.generation_mwh), 0) as renewable_pct
        from electric_generation g
        join fuel_type ft on ft.fuel_type_id = g.fuel_type_id
        group by g.ba_id
    ),
    location as (
        select
            ba_id,
            sum(latitude * weather_weight) / sum(weather_weight) as latitude,
            sum(longitude * weather_weight) / sum(weather_weight) as longitude
        from weather_location wl
        join ba_weather_location bwl on bwl.weather_location_id = wl.weather_location_id
        group by ba_id
    )
    select
        ba.ba_id,
        ba.ba_code,
        ba.ba_name,
        d.avg_demand_mwh,
        d.net_interchange_mwh,
        g.avg_generation_mwh,
        g.renewable_pct,
        l.latitude,
        l.longitude
    from balancing_authority ba
    join demand d on d.ba_id = ba.ba_id
    join generation g on g.ba_id = ba.ba_id
    join location l on l.ba_id = ba.ba_id
    """
    metrics = {
        "avg_demand_mwh": {"label": "Avg Demand (MWh)", "fmt": ",.0f", "unit": " MWh"},
        "renewable_pct": {"label": "Renewable %", "fmt": ".1f", "unit": "%"},
        "net_interchange_mwh": {
            "label": "Net Interchange (MWh)",
            "fmt": ",.0f",
            "unit": " MWh",
        },
    }
    return extract_data(sql), metrics


ba_metrics_df, ba_metrics = load_ba_metrics()


# BA tab - BA KPIs
@callback(
    Output(component_id="output-ba-kpi-metric-cleanest", component_property="children"),
    Output(component_id="output-ba-kpi-metric-demand", component_property="children"),
    Output(component_id="output-ba-kpi-metric-gen", component_property="children"),
    Output(component_id="output-ba-kpi-metric-top", component_property="children"),
    Output(component_id="output-ba-kpi-metric-bottom", component_property="children"),
    Input(component_id="input-ba-metric-dropdown", component_property="value"),
)
def update_ba_kpis(selected_metric):
    df = ba_metrics_df.dropna(subset=[selected_metric]).sort_values(
        selected_metric, ascending=False
    )
    metric_settings = ba_metrics[selected_metric]

    cleanest = ba_metrics_df.dropna(subset=["renewable_pct"]).sort_values(
        "renewable_pct", ascending=False
    )
    most_demand = ba_metrics_df.dropna(subset=["avg_demand_mwh"]).sort_values(
        "avg_demand_mwh", ascending=False
    )
    most_gen = ba_metrics_df.dropna(subset=["avg_generation_mwh"]).sort_values(
        "avg_generation_mwh", ascending=False
    )
    top_row = df.iloc[0]
    bottom_row = df.iloc[-1]

    kpi_style = {
        "display": "flex",
        "justifyContent": "space-between",
        "alignItems": "center",
        "width": "100%",
    }
    small_text_style = {"fontSize": "18px", "fontWeight": "normal"}

    cleanest_text = html.Div(
        [
            html.Span(cleanest.iloc[0]["ba_code"]),
            html.Span(
                f"{cleanest.iloc[0]['renewable_pct']:.2f}%",
                style=small_text_style,
            ),
        ],
        style=kpi_style,
    )
    most_demand_text = html.Div(
        [
            html.Span(most_demand.iloc[0]["ba_code"]),
            html.Span(
                f"{most_demand.iloc[0]["avg_demand_mwh"]:,.0f} MWh",
                style=small_text_style,
            ),
        ],
        style=kpi_style,
    )
    most_gen_text = html.Div(
        [
            html.Span(most_gen.iloc[0]["ba_code"]),
            html.Span(
                f"{most_gen.iloc[0]["avg_generation_mwh"]:,.0f} MWh",
                style=small_text_style,
            ),
        ],
        style=kpi_style,
    )
    top_text = html.Div(
        [
            html.Span(top_row["ba_code"]),
            html.Span(
                f"{top_row[selected_metric]:{metric_settings['fmt']}}{metric_settings['unit']}",
                style=small_text_style,
            ),
        ],
        style=kpi_style,
    )
    bottom_text = html.Div(
        [
            html.Span(bottom_row["ba_code"]),
            html.Span(
                f"{bottom_row[selected_metric]:{metric_settings['fmt']}}{metric_settings['unit']}",
                style=small_text_style,
            ),
        ],
        style=kpi_style,
    )
    return cleanest_text, most_demand_text, most_gen_text, top_text, bottom_text


# BA tab - BA map
@callback(
    Output(component_id="output-ba-metric-map", component_property="figure"),
    Input(component_id="input-ba-metric-dropdown", component_property="value"),
)
def update_ba_map(selected_metric):
    df = ba_metrics_df.dropna(subset=[selected_metric]).sort_values(
        selected_metric, ascending=False
    )
    metric_settings = ba_metrics[selected_metric]

    df = df.assign(bubble_size=df[selected_metric].abs())
    return px.scatter_geo(
        df,
        lat="latitude",
        lon="longitude",
        size="bubble_size",
        size_max=40,
        color=selected_metric if selected_metric == "net_interchange_mwh" else None,
        color_continuous_scale="RdBu",
        color_continuous_midpoint=0,
        hover_name="ba_name",
        hover_data={
            selected_metric: ":" + metric_settings["fmt"],
            "bubble_size": False,
            "latitude": False,
            "longitude": False,
        },
        scope="usa",
        title=f"BA Centroid Locations by {metric_settings["label"]}",
    )


# BA tab - BA bar
@callback(
    Output(component_id="output-ba-metric-bar", component_property="figure"),
    Input(component_id="input-ba-metric-dropdown", component_property="value"),
)
def update_ba_bar_chart(selected_metric):
    df = (
        ba_metrics_df.dropna(subset=[selected_metric])
        .sort_values(selected_metric, ascending=False)
        .head(10)
    )
    metric_settings = ba_metrics[selected_metric]

    return px.bar(
        df,
        x="ba_code",
        y=selected_metric,
        hover_name="ba_name",
        hover_data={
            "ba_code": False,
            selected_metric: ":" + metric_settings["fmt"],
        },
        labels={"ba_code": "BA", selected_metric: metric_settings["label"]},
        title=f"Top 10 BAs by {metric_settings["label"]}",
    )
