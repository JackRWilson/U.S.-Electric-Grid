import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from data import extract_data


# Pipeline tab
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
