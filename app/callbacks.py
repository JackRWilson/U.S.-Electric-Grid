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


# Weather tab - Weather KPIs
@callback(
    Output(component_id="output-weather-kpi-temp", component_property="children"),
    Output(component_id="output-weather-kpi-balance", component_property="children"),
    Output(component_id="output-weather-kpi-bal-demand", component_property="children"),
    Output(component_id="output-weather-kpi-demand", component_property="children"),
    Input(component_id="input-weather-ba-dropdown", component_property="value"),
)
def update_weather_kpis(selected_ba):
    ba_filter = f"where ba.ba_code = '{selected_ba}'" if selected_ba else ""

    sql = f"""
    with demand as (
        select
            ba_id,
            period, 
            demand_mwh
        from electric_demand
        where demand_mwh > 0
    ),
    temp as (
        select
            bwl.ba_id,
            w.period,
            sum(w.temp * bwl.weather_weight) / nullif(sum(bwl.weather_weight), 0) as temp
        from weather w
        inner join ba_weather_location bwl on bwl.weather_location_id = w.weather_location_id
        where w.temp is not null
        group by bwl.ba_id, w.period
    ),
    joined as (
        select
            demand.ba_id,
            temp.temp,
            demand.demand_mwh,
            demand.demand_mwh / nullif(avg(demand.demand_mwh) over (partition by demand.ba_id), 0) as demand_index
        from demand
        inner join temp on temp.ba_id = demand.ba_id and temp.period = demand.period
        inner join balancing_authority ba on ba.ba_id = demand.ba_id
        {ba_filter}
    )
    select
        round(temp / 2) * 2 as temp_bin,
        count(*) as obs_hours,
        sum(temp) as temp_sum,
        avg(demand_index) as avg_demand_index,
        avg(demand_mwh) as avg_demand
    from joined
    where temp is not null
    group by temp_bin
    order by temp_bin
    """
    df = extract_data(sql)
    if df["obs_hours"].sum() > 0:
        avg_temp = f"{df["temp_sum"].sum() / df["obs_hours"].sum():.1f}°F"
    else:
        avg_temp = "N/A"

    if selected_ba:
        min_hours = 10
    else:
        min_hours = 50
    valid_df = df[df["obs_hours"] >= min_hours].reset_index(drop=True)
    if valid_df.empty:
        balance_temp = "N/A"
        balance_demand = "N/A"
    else:
        min_index = valid_df["avg_demand_index"].idxmin()
        on_edge = min_index in (0, len(valid_df) - 1)
        if on_edge:
            balance_temp = "N/A"
            balance_demand = "N/A"
        else:
            row = valid_df.loc[min_index]
            balance_temp = f"{row["temp_bin"]:.0f}°F"
            if selected_ba:
                balance_demand = f"{row["avg_demand"]:,.0f} MWh"
            else:
                balance_demand = f"{row["avg_demand_index"]:.2f}x Average"

    if selected_ba:
        sql = f"""
        select
            avg(d.demand_mwh) as avg_demand
        from electric_demand d
        inner join balancing_authority ba on ba.ba_id = d.ba_id
        where d.demand_mwh > 0
            and ba.ba_code = '{selected_ba}'
        group by ba.ba_code
        """
    else:
        sql = """
        select
            avg(total_mwh) as avg_demand
        from (
            select 
                period,
                sum(demand_mwh) as total_mwh
            from electric_demand
            where demand_mwh > 0
            group by period
        ) hourly_totals
        """
    df = extract_data(sql)
    if df.empty:
        avg_demand = "N/A"
    else:
        avg_demand = f"{df["avg_demand"].iloc[0]:,.0f} MWh"

    return avg_temp, balance_temp, balance_demand, avg_demand


# Weather tab - Demand / temp scatter
@callback(
    Output("output-weather-demand-scatter", "figure"),
    Input("input-weather-ba-dropdown", "value"),
)
def update_weather_demand_scatter(selected_ba):
    base_sql = """
    with demand as (
        select ba_id, period, demand_mwh
        from electric_demand
        where demand_mwh > 0
    ),
    temp as (
        select
            bwl.ba_id,
            w.period,
            sum(w.temp * bwl.weather_weight) / nullif(sum(bwl.weather_weight), 0) as temp
        from weather w
        inner join ba_weather_location bwl on bwl.weather_location_id = w.weather_location_id
        where w.temp is not null
        group by bwl.ba_id, w.period
    )
    """

    fig = go.Figure()

    if selected_ba:
        sql = base_sql + f"""
        select
            ba.ba_code,
            ba.ba_name,
            demand.period,
            temp.temp,
            demand.demand_mwh
        from demand
        inner join temp on temp.ba_id = demand.ba_id and temp.period = demand.period
        inner join balancing_authority ba on ba.ba_id = demand.ba_id
        where temp.temp is not null
          and ba.ba_code = '{selected_ba}'
        order by demand.period;
        """
        df = extract_data(sql)

        fig.add_trace(
            go.Scattergl(
                x=df["temp"],
                y=df["demand_mwh"],
                mode="markers",
                marker={"opacity": 0.25, "size": 5, "color": "#636efa"},
                text=df["period"],
                hovertemplate="%{text}<br>"
                + "%{x:.1f}°F<br>"
                + "%{y:,.0f} MWh"
                + "<extra></extra>",
                name="Hourly Demand",
            )
        )

        df["temp_bin"] = (df["temp"] / 2).round() * 2
        trend = (
            df.groupby("temp_bin")["demand_mwh"].agg(["median", "size"]).reset_index()
        )
        trend = trend[trend["size"] >= 10]
        fig.add_trace(
            go.Scatter(
                x=trend["temp_bin"],
                y=trend["median"],
                mode="lines",
                line={"color": "#EF553B", "width": 3},
                name="Median by Temperature",
            )
        )
        y_title = "Demand (MWh)"

    else:
        sql = base_sql + """
        , joined as (
            select
                demand.ba_id,
                round(temp.temp / 2) * 2 as temp_bin,
                demand.demand_mwh / nullif(avg(demand.demand_mwh) over (partition by demand.ba_id), 0) as demand_index
            from demand
            inner join temp on temp.ba_id = demand.ba_id and temp.period = demand.period
            where temp.temp is not null
        )
        select
            temp_bin,
            percentile_cont(0.5) within group (order by demand_index) as median_index,
            percentile_cont(0.1) within group (order by demand_index) as p10,
            percentile_cont(0.9) within group (order by demand_index) as p90,
            count(*) as obs_hours,
            count(distinct ba_id) as n_bas
        from joined
        where demand_index is not null
        group by temp_bin
        having count(*) >= 50
        order by temp_bin;
        """
        df = extract_data(sql)

        fig.add_trace(
            go.Scatter(
                x=df["temp_bin"],
                y=df["p90"],
                mode="lines",
                line={"width": 0},
                showlegend=False,
                hoverinfo="skip",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df["temp_bin"],
                y=df["p10"],
                mode="lines",
                line={"width": 0},
                fill="tonexty",
                fillcolor="rgba(99,110,250,0.2)",
                name="10-90th percentile",
                hoverinfo="skip",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df["temp_bin"],
                y=df["median_index"],
                mode="lines+markers",
                line={"color": "#EF553B", "width": 3},
                customdata=df[["obs_hours", "n_bas"]],
                hovertemplate="%{x}°F<br>"
                + "Median Index: %{y:.2f}<br>"
                + "Hours: %{customdata[0]:,}<br>"
                + "BAs: %{customdata[1]}"
                + "<extra></extra>",
                name="Median Demand Index",
            )
        )
        y_title = "Demand Index (1.0 = BA average)"

    fig.update_layout(
        xaxis_title="Temperature (°F)",
        yaxis_title=y_title,
        legend={"orientation": "h", "y": 1.08},
    )
    return fig


# Weather tab - Demand/Gen by weather code
@callback(
    Output(component_id="output-weather-code-bar", component_property="figure"),
    Input(component_id="input-weather-ba-dropdown", component_property="value"),
)
def update_weather_code_bar(selected_ba):
    ba_filter = f"and ba.ba_code = '{selected_ba}'" if selected_ba else ""

    sql = f"""
    with demand as (
        select 
            ba_id, 
            period, 
            demand_mwh
        from electric_demand
        where demand_mwh > 0
    ),
    generation as (
        select 
            ba_id, 
            period, 
            sum(generation_mwh) as generation_mwh
        from electric_generation
        group by ba_id, period
    ),
    wcode as (
        select distinct on (bwl.ba_id, w.period)
            bwl.ba_id,
            w.period,
            w.weather_code
        from weather w
        inner join ba_weather_location bwl on bwl.weather_location_id = w.weather_location_id
        group by bwl.ba_id, w.period, w.weather_code
        order by bwl.ba_id, w.period, sum(bwl.weather_weight) desc
    )
    select
        wcode.weather_code,
        avg(demand.demand_mwh) as avg_demand_mwh,
        avg(generation.generation_mwh) as avg_generation_mwh,
        count(*) as obs_hours
    from demand
    inner join generation on generation.ba_id = demand.ba_id and generation.period = demand.period
    inner join wcode on wcode.ba_id = demand.ba_id and wcode.period = demand.period
    inner join balancing_authority ba on ba.ba_id = demand.ba_id
    {ba_filter}
    group by wcode.weather_code
    order by wcode.weather_code;
    """
    df = extract_data(sql)
    return px.bar(
        df.melt(
            id_vars=["weather_code", "obs_hours"],
            value_vars=["avg_demand_mwh", "avg_generation_mwh"],
            var_name="Metric",
            value_name="mwh",
        ).sort_values(by="mwh"),
        x="weather_code",
        y="mwh",
        color="Metric",
        barmode="group",
        labels={
            "weather_code": "Weather Code",
            "mwh": "MWh",
            "obs_hours": "Hours Observed",
            "avg_demand_mwh": "Avg Demand",
            "avg_generation_mwh": "Avg Generation",
        },
        hover_data=["obs_hours"],
    )


# Weather tab - Renewables scatter
@callback(
    Output("output-weather-renewables-scatter", "figure"),
    Input("input-weather-ba-dropdown", "value"),
)
def update_weather_renewables_scatter(selected_ba):
    ba_filter = f"where ba.ba_code = '{selected_ba}'" if selected_ba else ""

    if selected_ba:
        wind_val = "gen.wind_mwh::numeric"
        solar_val = "gen.solar_mwh::numeric"
        wind_title, solar_title = "Wind Generation (MWh)", "Solar Generation (MWh)"
    else:
        wind_val = "gen.wind_mwh::numeric / nullif(max(gen.wind_mwh) over (partition by gen.ba_id), 0)"
        solar_val = "gen.solar_mwh::numeric / nullif(max(gen.solar_mwh) over (partition by gen.ba_id), 0)"
        wind_title, solar_title = (
            "Wind Generation Index",
            "Solar Generation Index",
        )

    sql = f"""
    with weath as (
        select
            bwl.ba_id,
            w.period,
            sum(w.wind_speed_120m * bwl.weather_weight) / nullif(sum(bwl.weather_weight), 0) as wind_speed,
            sum(w.total_cloud_cover * bwl.weather_weight) / nullif(sum(bwl.weather_weight), 0) as cloud_cover
        from weather w
        inner join ba_weather_location bwl on bwl.weather_location_id = w.weather_location_id
        where w.wind_speed_120m is not null
        and w.total_cloud_cover is not null
        group by bwl.ba_id, w.period
    ),
    gen as (
        select
            eg.ba_id,
            eg.period,
            sum(case when ft.fuel_type_code = 'WND' then eg.generation_mwh end) as wind_mwh,
            sum(case when ft.fuel_type_code = 'SUN' then eg.generation_mwh end) as solar_mwh
        from electric_generation eg
        inner join fuel_type ft on ft.fuel_type_id = eg.fuel_type_id
        group by eg.ba_id, eg.period
    )
    select
        ba.ba_code,
        weath.period,
        weath.wind_speed,
        weath.cloud_cover,
        {wind_val} as wind_value,
        {solar_val} as solar_value
    from weath
    inner join gen on gen.ba_id = weath.ba_id and gen.period = weath.period
    inner join balancing_authority ba on ba.ba_id = weath.ba_id
    {ba_filter}
    order by weath.period;
    """
    df = extract_data(sql)

    wind = df.dropna(subset=["wind_value"]).query("wind_value >= 0")
    solar = df.dropna(subset=["solar_value"]).query("solar_value > 0")

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=(
            "Wind Generation vs 120m Wind Speed",
            "Solar Generation vs Cloud Cover",
        ),
    )
    fig.add_trace(
        go.Scattergl(
            x=wind["wind_speed"],
            y=wind["wind_value"],
            mode="markers",
            text=wind["period"],
            hovertemplate=(
                "%{text}<br>"
                + "Wind Speed: %{x:.1f}<br>"
                + "Wind Value: %{y:.2f}"
                + "<extra></extra>"
            ),
            marker={"opacity": 0.3},
            showlegend=False,
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scattergl(
            x=solar["cloud_cover"],
            y=solar["solar_value"],
            mode="markers",
            text=solar["period"],
            hovertemplate=(
                "%{text}<br>"
                + "Cloud Cover: %{x:.1f}%<br>"
                + "Solar Value: %{y:.2f}"
                + "<extra></extra>"
            ),
            marker={"opacity": 0.3},
            showlegend=False,
        ),
        row=1,
        col=2,
    )
    fig.update_xaxes(title_text="Wind Speed (120m)", row=1, col=1)
    fig.update_xaxes(title_text="Cloud Cover (%)", row=1, col=2)
    fig.update_yaxes(title_text=wind_title, row=1, col=1)
    fig.update_yaxes(title_text=solar_title, row=1, col=2)
    return fig
