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
    with generation as (
        select
            eg.period,	
            sum(generation_mwh) as total_generation_mwh
        from electric_generation eg
        inner join electric_demand ed on ed.period = eg.period
        group by eg.period
        order by eg.period desc
        limit 1
    ),
    demand as (
        select
            ed.period,	
            sum(demand_mwh) as total_demand_mwh
        from electric_demand ed
        inner join electric_generation eg on eg.period = ed.period
        group by ed.period
        order by ed.period desc
        limit 1
    ),
    fuel as (
        select
            eg.period,	
            sum(generation_mwh) as total_generation_mwh,
            ft.fuel_type_name
        from electric_generation eg
        inner join electric_demand ed on ed.period = eg.period
        join fuel_type ft on ft.fuel_type_id = eg.fuel_type_id
        where eg.period = (
            select max(eg.period)
            from electric_generation eg
            inner join electric_demand ed on ed.period = eg.period
            )
        group by eg.period, ft.fuel_type_name
        order by eg.period desc, total_generation_mwh desc
        limit 1
    )
    select
        demand.period,
        generation.total_generation_mwh,
        demand.total_demand_mwh,
        fuel.total_generation_mwh as gen_from_fuel,
        fuel.fuel_type_name
    from demand
    inner join generation on generation.period = demand.period
    inner join fuel on fuel.period = demand.period
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
