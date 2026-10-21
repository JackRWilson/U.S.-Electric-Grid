import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from data import extract_data


# Pipeline tab - ba map
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
            colorscale=[[0, "orange"], [1, "orange"]],
            showscale=False,
            marker_line_color="black",
            marker_line_width=1,
            name="Missouri",
        )
    )

    east_ok_lat = [37.0, 37.0, 33.6, 33.8, 37.0]
    east_ok_lon = [-98.0, -94.6, -94.4, -98.0, -95.0]

    fig.add_trace(
        go.Scattergeo(
            lat=east_ok_lat,
            lon=east_ok_lon,
            fill="toself",
            fillcolor="orange",
            line={"color": "black", "width": 1},
            mode="lines",
            name="Eastern Oklahoma",
            showlegend=False,
            hoverinfo="skip",
        )
    )
    fig.update_geos(
        center={
            "lat": df["latitude"].mean(),
            "lon": df["longitude"].mean(),
        },
        projection_scale=4,
        showcountries=True,
        countrycolor="white",
        showland=True,
        landcolor="lightgray",
    )
    fig.update_traces(
        selector={"type": "scattergeo", "mode": "markers+text"},
        textposition="bottom right",
        textfont={
            "size": 12,
            "color": "black",
        },
        marker={
            "size": 12,
            "color": "red",
            "line": {"color": "white", "width": 1},
        },
    )
    fig.data = (fig.data[1], fig.data[2], fig.data[0])
    fig.update_layout(height=800)
    return fig


# National picture tab - KPIs
def nat_pic_kpis():
    sql = """
    with latest_period as (
        select max(eg.period) as period
        from electric_generation eg
        inner join electric_demand ed on ed.period = eg.period
    ),
    generation as (
        select
            eg.period,	
            sum(generation_mwh) as total_generation_mwh
        from electric_generation eg
        inner join latest_period lp on lp.period = eg.period
        group by eg.period
    ),
    demand as (
        select
            ed.period,	
            sum(demand_mwh) as total_demand_mwh
        from electric_demand ed
        inner join latest_period lp on lp.period = ed.period
        group by ed.period
    ),
    fuel as (
        select
            eg.period,	
            sum(generation_mwh) as total_generation_mwh,
            ft.fuel_type_name
        from electric_generation eg
        inner join latest_period lp on lp.period = eg.period
        inner join fuel_type ft on ft.fuel_type_id = eg.fuel_type_id
        group by eg.period, ft.fuel_type_name
        order by total_generation_mwh desc
        limit 1
    )
    select
        latest_period.period,
        generation.total_generation_mwh,
        demand.total_demand_mwh,
        fuel.total_generation_mwh as gen_from_fuel,
        fuel.fuel_type_name
    from latest_period
    join generation on generation.period = latest_period.period
    join demand on demand.period = latest_period.period
    join fuel on fuel.period = latest_period.period
    """
    df = extract_data(sql)

    row = df.iloc[0]
    period = pd.to_datetime(row["period"]).strftime("%b %d, %Y %I:%M %p")
    total_gen = f"{float(row["total_generation_mwh"]):,.0f} MWh"
    total_demand = f"{float(row["total_demand_mwh"]):,.0f} MWh"
    fuel_name = row["fuel_type_name"]
    gen_from_fuel = f"{float(row["gen_from_fuel"]):,.0f} MWh"

    return period, total_gen, total_demand, fuel_name, gen_from_fuel


# National picture tab - demand graph
def nat_pic_demand_line_graph():
    sql = """
    select 
        period,	
        sum(demand_mwh) as total_mwh
    from electric_demand
    group by period
    order by period
    """
    df = extract_data(sql)

    return px.line(
        df,
        x="period",
        y="total_mwh",
        labels={"period": "Time", "total_mwh": "Total Demand (MWh)"},
        title="Total Demand",
    )


# National picture tab - fuel type graph
def nat_pic_fuel_graph():
    sql = """
    select
        sum(eg.generation_mwh) as total_generation_mwh,
        ft.fuel_type_code,
        ft.fuel_type_name 
    from electric_generation eg
    join fuel_type ft on ft.fuel_type_id = eg.fuel_type_id
    group by ft.fuel_type_code, ft.fuel_type_name
    order by total_generation_mwh desc
    """
    df = extract_data(sql)

    return px.bar(
        df,
        x="fuel_type_name",
        y="total_generation_mwh",
        labels={
            "fuel_type_name": "Fuel Type",
            "total_generation_mwh": "Total Generation (MWh)",
        },
        title="Total Generation by Fuel",
    )


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
    )
    demand_min = df["avg_demand_kw_per_person"].min()
    demand_max = df["avg_demand_kw_per_person"].max()
    demand_padding = max((demand_max - demand_min) * 0.08, demand_max * 0.03)
    fig.update_yaxes(
        range=[max(0, demand_min - demand_padding), demand_max + demand_padding],
    )
    fit = px.get_trendline_results(fig).iloc[0]["px_fit_results"]
    return fig, fit


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


def pop_inc_demand_pop_scatter():
    fig, _ = pop_inc_scatter(
        x="total_pop",
        title="Per-Person Demand vs. Population",
        x_label="Population",
    )
    return fig


def pop_inc_demand_inc_scatter():
    fig, _ = pop_inc_scatter(
        x="avg_income_per_capita",
        title="Per-Person Demand vs. Income",
        x_label="Population-weighted County Income Per Capita ($)",
    )
    return fig
