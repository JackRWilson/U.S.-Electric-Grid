import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from styles import COLORS, DATA_COLORS, FONTS, PLOTLY_AXIS_STYLE, PLOTLY_LAYOUT_STYLE

from data import extract_data, get_temp_balance_number

LATEST_COMPLETE_PERIOD_CTE = """
latest_complete_period as (
    select 
        coverage.period
    from (
        select
            coalesce(d.period, g.period) as period,
            count(distinct case
                when d.demand_mwh is not null then d.ba_id
            end) as demand_bas,
            count(distinct case
                when g.generation_mwh is not null then g.ba_id
            end) as generation_bas,
            count(distinct case
                when d.demand_mwh is not null and g.generation_mwh is not null
                    then d.ba_id
            end) as matched_bas
        from electric_demand d
        full outer join electric_generation g on g.period = d.period and g.ba_id = d.ba_id
        group by coalesce(d.period, g.period)
    ) coverage
    where coverage.demand_bas > 0
        and coverage.demand_bas = coverage.generation_bas
        and coverage.demand_bas = coverage.matched_bas
    order by coverage.period desc
    limit 1
)
"""


# Overview tab - BA map
def overview_ba_map(df):
    fig = px.scatter_geo(
        df,
        lat="latitude",
        lon="longitude",
        size="avg_demand_mwh",
        size_max=40,
        color="renewable_pct",
        color_continuous_scale=["#fde2c4", DATA_COLORS["green"]],
        range_color=[0, 100],
        scope="usa",
        hover_name="ba_name",
        hover_data={
            "ba_code": True,
            "avg_demand_mwh": ":,.0f",
            "renewable_pct": ":.1f",
            "latitude": False,
            "longitude": False,
            "avg_generation_mwh": False,
            "net_interchange_mwh": False,
        },
        labels={
            "ba_code": "BA",
            "avg_demand_mwh": "Average Demand (MWh)",
            "renewable_pct": "Renewable Generation (%)",
        },
        title="Balancing Authorities - Demand & Renewable Share",
    )
    fig.update_geos(
        bgcolor="rgba(0,0,0,0)",
        showocean=False,
        showlakes=False,
        showland=True,
        landcolor=COLORS["border"],
        showcountries=True,
        countrycolor=COLORS["surface"],
        showsubunits=True,
        subunitcolor=COLORS["surface"],
        subunitwidth=0.5,
        showframe=False,
    )
    fig.update_traces(
        marker={"line": {"width": 0.75, "color": COLORS["surface"]}},
    )
    fig.update_layout(
        {
            **PLOTLY_LAYOUT_STYLE,
            "margin": {"l": 0, "r": 0, "t": 60, "b": 8},
            "coloraxis_colorbar": {
                "title": "Renewable<br>generation (%)<br> <br> ",
                "tickfont": {"color": COLORS["text"], "family": FONTS["mono"]},
                "outlinewidth": 0,
            },
        }
    )
    return fig


# Overview tab - Temp graph
def overview_temp_graph(temp_figure, balance_temp):
    balance_temp_number = get_temp_balance_number(balance_temp)

    if balance_temp_number is not None:
        temp_figure.add_vline(
            x=balance_temp_number,
            line_dash="dash",
            line_color=DATA_COLORS["orange"],
            annotation_text=f"  Balance {balance_temp}",
            annotation_position="top right",
            annotation_font_color=DATA_COLORS["orange"],
        )

    temp_figure.update_layout(
        title="Demand vs. Temperature",
        yaxis_title="Demand Index",
        showlegend=False,
    )
    return temp_figure


# Pipeline tab - BA map
def pipeline_ba_map():
    sql = """
    select
        ba.ba_code,
        ba.ba_name,
        w.temp,
        wl.latitude,
        wl.longitude,
        bwl.weather_weight
    from weather w
    join weather_location wl on wl.weather_location_id = w.weather_location_id
    join ba_weather_location bwl on bwl.weather_location_id = wl.weather_location_id
    join balancing_authority ba on ba.ba_id = bwl.ba_id
    where ba_code = 'AECI'
    order by period, ba_code
    limit 3
    """
    df = extract_data(sql)

    fig = px.scatter_geo(
        df,
        lat="latitude",
        lon="longitude",
        scope="usa",
        hover_name="ba_code",
        hover_data=["ba_name", "latitude", "longitude", "weather_weight"],
        text=df.apply(
            lambda row: (
                f"Weight: {row['weather_weight']:.1%}<br>" f"Temp: {row['temp']}°F"
            ),
            axis=1,
        ),
    )
    fig.add_trace(
        go.Choropleth(
            locations=["MO"],
            z=[1],
            locationmode="USA-states",
            colorscale=[[0, DATA_COLORS["blue"]], [1, DATA_COLORS["blue"]]],
            showscale=False,
            marker_line_color="black",
            marker_line_width=1,
        )
    )

    # Top left, top right, bottom right, bottom left, top left
    east_ok_lat = [37.0, 37.0, 33.6, 33.8, 37.0]  # NS
    east_ok_lon = [-98.0, -94.5, -94.4, -98.0, -98.0]  # EW

    fig.add_trace(
        go.Scattergeo(
            lat=east_ok_lat,
            lon=east_ok_lon,
            fill="toself",
            fillcolor=DATA_COLORS["blue"],
            line={"color": "black", "width": 0},
            mode="lines",
            showlegend=False,
            hoverinfo="skip",
        )
    )
    fig.update_geos(
        center={
            "lat": df["latitude"].mean(),
            "lon": df["longitude"].mean(),
        },
        projection_scale=3.2,
        showcountries=True,
        countrycolor="white",
        showland=True,
        landcolor=COLORS["surface"],
        showsubunits=True,
        subunitcolor=COLORS["border_strong"],
        subunitwidth=0.5,
        showframe=False,
    )
    fig.update_traces(
        selector={"type": "scattergeo", "mode": "markers+text"},
        textposition=["bottom left", "bottom right", "bottom right"],
        textfont={
            "size": 12,
            "color": "white",
        },
        marker={
            "size": 10,
            "color": "white",
            "line": {"color": "black", "width": 1},
        },
    )
    fig.data = (fig.data[1], fig.data[2], fig.data[0])
    fig.update_layout(
        {
            **PLOTLY_LAYOUT_STYLE,
            "margin": {"l": 0, "r": 0, "t": 0, "b": 0},
            "autosize": True,
        }
    )
    return fig


# National picture tab - KPIs
def nat_pic_kpis():
    sql = f"""
    with {LATEST_COMPLETE_PERIOD_CTE},
    generation as (
        select
            sum(eg.generation_mwh) as total_generation_mwh
        from electric_generation eg
        inner join latest_complete_period lp on lp.period = eg.period
    ),
    demand as (
        select
            sum(ed.demand_mwh) as total_demand_mwh
        from electric_demand ed
        inner join latest_complete_period lp on lp.period = ed.period
    ),
    fuel as (
        select
            sum(eg.generation_mwh) as gen_from_fuel,
            ft.fuel_type_name
        from electric_generation eg
        inner join latest_complete_period lp on lp.period = eg.period
        inner join fuel_type ft on ft.fuel_type_id = eg.fuel_type_id
        group by ft.fuel_type_name
        order by gen_from_fuel desc
        limit 1
    )
    select
        latest_complete_period.period,
        generation.total_generation_mwh,
        demand.total_demand_mwh,
        fuel.gen_from_fuel,
        fuel.fuel_type_name
    from latest_complete_period
    cross join generation
    cross join demand
    cross join fuel
    """
    df = extract_data(sql)

    if df.empty:
        return "No complete period", "N/A", "N/A", "N/A", "N/A"

    row = df.iloc[0]
    period = (
        pd.to_datetime(row["period"], utc=True)
        .tz_convert("America/Chicago")
        .strftime("%b %d, %Y %I:%M %p")
    )
    total_gen = f"{float(row["total_generation_mwh"]):,.0f} MWh"
    total_demand = f"{float(row["total_demand_mwh"]):,.0f} MWh"
    fuel_name = row["fuel_type_name"]
    gen_from_fuel = f"{float(row["gen_from_fuel"]):,.0f} MWh"

    return period, total_gen, total_demand, fuel_name, gen_from_fuel


# National picture tab - Demand graph
def nat_pic_demand_line_graph():
    sql = f"""
    with {LATEST_COMPLETE_PERIOD_CTE}
    select 
        period, 
        sum(demand_mwh) as total_mwh
    from electric_demand
    where period between
        (select period - interval '14 days' from latest_complete_period)
        and (select period from latest_complete_period)
    group by period
    order by period;
    """
    df = extract_data(sql)
    df["period"] = pd.to_datetime(df["period"], utc=True).dt.tz_convert(
        "America/Chicago"
    )

    fig = px.line(
        df,
        x="period",
        y="total_mwh",
        labels={"period": "Time", "total_mwh": "Total Demand (MWh)"},
        title="Demand (Last 14 Days)",
        color_discrete_sequence=[DATA_COLORS["blue"]],
    )
    fig.update_xaxes(**PLOTLY_AXIS_STYLE)
    fig.update_layout(**PLOTLY_LAYOUT_STYLE)
    return fig


# National picture tab - Fuel type graph
def nat_pic_fuel_graph():
    sql = f"""
    with {LATEST_COMPLETE_PERIOD_CTE},
    fuel_totals as (
        select
            ft.fuel_type_name,
            sum(g.generation_mwh) as total_generation_mwh
        from electric_generation g
        join fuel_type ft on ft.fuel_type_id = g.fuel_type_id
        where g.period between
            (select period - interval '14 days' from latest_complete_period)
            and (select period from latest_complete_period)
        group by ft.fuel_type_name
    ),
    rank as (
        select
            fuel_type_name,
            total_generation_mwh,
            row_number() over (order by total_generation_mwh desc) as fuel_rank
        from fuel_totals
    ),
    bucket as (
    	select
	    	case
	            when fuel_rank <= 7 and fuel_type_name <> 'Other'
	                then fuel_type_name
	            else 'Other (combined)'
	        end as fuel_group,
	        total_generation_mwh
		from rank
)
    select
        fuel_group as fuel_type_name,
        sum(total_generation_mwh) as total_generation_mwh
    from bucket
    group by fuel_group
    order by sum(total_generation_mwh) desc
    """
    df = extract_data(sql)

    fig = px.bar(
        df,
        x="fuel_type_name",
        y="total_generation_mwh",
        labels={
            "fuel_type_name": "Fuel Type",
            "total_generation_mwh": "Total Generation (MWh)",
        },
        title="Generation by Fuel (Last 14 Days)",
        color_discrete_sequence=[DATA_COLORS["green"]],
    )
    fig.update_traces(
        hovertemplate="%{y}<br>" + "%{x:,.0f} MWh" + "<extra></extra>",
    )
    fig.update_xaxes(**PLOTLY_AXIS_STYLE, title="Total Generation (MWh)")
    fig.update_yaxes(
        **PLOTLY_AXIS_STYLE,
        title=None,
    )
    fig.update_layout(**PLOTLY_LAYOUT_STYLE)

    return fig


# Pop and income tab - Demand, pop, income estimates
def pop_inc_ba_data():
    sql = """
    with demand as (
        select
            ba_id,
            avg(demand_mwh) as avg_demand_mw
        from electric_demand
        where demand_mwh > 0
        group by ba_id
    ),
    demo as (
        select
            ba.ba_id,
            ba.ba_code,
            ba.ba_name,
            sum(c.est_population_2024) as total_pop,
            sum(c.personal_income_per_capita::numeric * c.est_population_2024)
                / nullif(sum(c.est_population_2024), 0) as avg_income_per_capita
        from county c
        join ba_county bc on bc.county_id = c.county_id
        join balancing_authority ba on ba.ba_id = bc.ba_id
        group by ba.ba_id, ba.ba_code, ba.ba_name
    )
    select
        demo.ba_code,
        demo.ba_name,
        demo.total_pop,
        demo.avg_income_per_capita,
        demand.avg_demand_mw,
        demand.avg_demand_mw * 1000 / demo.total_pop as avg_demand_kw_per_person
    from demand
    join demo on demo.ba_id = demand.ba_id
    where demo.total_pop >= 100000
        and demo.avg_income_per_capita is not null
    order by demo.ba_code;
    """
    return extract_data(sql)


# Pop and income tab - General scatter function
def pop_inc_scatter(x, title, x_label):
    df = pop_inc_ba_data()
    fig = px.scatter(
        df,
        x=x,
        y="avg_demand_kw_per_person",
        hover_name="ba_code",
        hover_data=[
            "ba_name",
            "avg_demand_kw_per_person",
            "total_pop",
            "avg_income_per_capita",
        ],
        trendline="ols",
        labels={
            x: x_label,
            "avg_demand_kw_per_person": "Avg Hourly Demand/Person (kW/person)",
            "total_pop": "Population",
            "avg_income_per_capita": "Income Per Capita ($)",
        },
        title=title,
        color_discrete_sequence=[DATA_COLORS["blue"]],
        trendline_color_override=COLORS["accent_light"],
    )
    demand_min = df["avg_demand_kw_per_person"].min()
    demand_max = df["avg_demand_kw_per_person"].max()
    demand_padding = max((demand_max - demand_min) * 0.08, demand_max * 0.03)
    fig.update_yaxes(
        range=[max(0, demand_min - demand_padding), demand_max + demand_padding],
        **PLOTLY_AXIS_STYLE,
    )
    fig.update_xaxes(**PLOTLY_AXIS_STYLE)
    fig.update_layout(**PLOTLY_LAYOUT_STYLE)
    fit = px.get_trendline_results(fig).iloc[0]["px_fit_results"]
    return fig, fit


# Pop and income tab - KPIs
def pop_inc_kpis():
    _, population_fit = pop_inc_scatter(
        x="total_pop",
        title="Per-Person Demand vs. Population",
        x_label="Population",
    )
    _, income_fit = pop_inc_scatter(
        x="avg_income_per_capita",
        title="Per-Person Demand vs. Income",
        x_label="Population-weighted County Income Per Capita ($)",
    )
    return (
        f"{income_fit.rsquared:.2f}",
        f"{population_fit.rsquared:.2f}",
        f"{income_fit.params[1] * 10_000 * 8.76:+,.3f} MWh/person/year",
        f"{population_fit.params[1] * 100_000 * 8.76:+,.3f} MWh/person/year",
    )


# Pop and income tab - Pop scatter
def pop_inc_demand_pop_scatter():
    fig, _ = pop_inc_scatter(
        x="total_pop",
        title="Per-Person Demand vs. Population",
        x_label="Population",
    )
    return fig


# Pop and income tab - Income scatter
def pop_inc_demand_inc_scatter():
    fig, _ = pop_inc_scatter(
        x="avg_income_per_capita",
        title="Per-Person Demand vs. Income",
        x_label="Population-weighted County Income Per Capita ($)",
    )
    return fig
