import callbacks  # noqa: F401
from dash import dcc, html
from graphs import (
    nat_pic_demand_line_graph,
    nat_pic_fuel_graph,
    nat_pic_kpis,
    pipeline_ba_map,
)
from init_app import app
from inputs import ba_metric_dropdown, data_ba_dropdown, weather_ba_dropdown
from tables import count_bas_covered, kpi_card, render_grid, render_table

from data import get_next_run_time, render_latest_completion


def layout():
    tab_style = {
        "flex": "0 0 auto",
        "height": "34px",
        "minHeight": "0",
        "lineHeight": "34px",
        "padding": "0 12px",
        "fontSize": "14px",
        "whiteSpace": "nowrap",
        "overflow": "hidden",
        "textOverflow": "ellipsis",
        "borderLeft": "4px solid transparent",
    }
    tab_selected_style = {
        **tab_style,
        "backgroundColor": "#1975FA",
        "color": "white",
        "borderLeft": "4px solid #0b4fb3",
    }

    kpi_style = {
        "display": "flex",
        "gap": "16px",
        "marginBottom": "16px",
    }

    overview_tab = dcc.Tab(
        label="Overview",
        style=tab_style,
        selected_style=tab_selected_style,
        children=[
            html.Section(
                [
                    html.H1("Overview"),
                    html.P(
                        "Analysis of U.S. Energy generation and demand and how weather, population, and income play a role."
                    ),
                    html.H1("Questions"),
                    html.P(
                        "1. If we can (somewhat) accurately predict weather can that be mapped to electricity/energy usage?"
                    ),
                    html.P("2. How does energy demand and generation vary by area?"),
                    html.P(
                        "3. How does weather affect electricity demand and renewable energy generation?"
                    ),
                    html.P(
                        "4. How does population of an area impact its electricity generation and consumption?"
                    ),
                    html.P(
                        "5. Do areas with higher income use more electricity? How much more?"
                    ),
                    html.H1("Key Takeaways"),
                    html.P("..."),
                    html.H1("Limitations"),
                    html.P(
                        """Balance Authorities can cover very large areas, so their location was 
                        approximated. This includes BA to weather mapping as well."""
                    ),
                    html.H1("Next Steps"),
                    html.P(
                        "Dig into how precipitation, rain, snow, and wind speed affect energy generation."
                    ),
                    html.P(
                        "Add solar UV to schema and data and see how UV affects solar generation."
                    ),
                ]
            )
        ],
    )
    method_tab = dcc.Tab(label="Methodology", disabled=True, style=tab_style)
    # data_tab = dcc.Tab(
    #     label="Data",
    #     style=tab_style,
    #     selected_style=tab_selected_style,
    #     children=[
    #         html.Section(
    #             [
    #                 html.H1("Data"),
    #                 html.P(
    #                     "Seven different data sources are combined to create a comprehensive electricity, county, income, and population dataset. The final schema consists of 9 relational tables."
    #                 ),
    #                 html.H1("Tables"),
    #                 render_grid(
    #                     [
    #                         render_table(
    #                             table="Demand",
    #                             db_table="electric_demand",
    #                             order_by="period",
    #                             api_name="demand",
    #                         ),
    #                         render_table(
    #                             table="Generation",
    #                             db_table="electric_generation",
    #                             order_by="period",
    #                             api_name="generation",
    #                         ),
    #                         render_table(
    #                             table="Weather",
    #                             db_table="weather",
    #                             order_by="period",
    #                             api_name="weather",
    #                         ),
    #                         render_table(
    #                             table="County",
    #                             db_table="county",
    #                         ),
    #                         render_table(
    #                             table="Balancing Authority",
    #                             db_table="balancing_authority",
    #                         ),
    #                         render_table(
    #                             table="Fuel Type",
    #                             db_table="fuel_type",
    #                         ),
    #                         render_table(
    #                             table="Weather Location",
    #                             db_table="weather_location",
    #                         ),
    #                         render_table(
    #                             table="BA Weather Location",
    #                             db_table="ba_weather_location",
    #                         ),
    #                         render_table(
    #                             table="BA County",
    #                             db_table="ba_county",
    #                         ),
    #                     ]
    #                 ),
    #                 html.Section(
    #                     [
    #                         kpi_card("BAs Covered", value=count_bas_covered()),
    #                         kpi_card(
    #                             "Date Range", value_id="output-data-kpi-date-range"
    #                         ),
    #                         kpi_card(
    #                             "Total Demand", value_id="output-data-kpi-total-mwh"
    #                         ),
    #                     ],
    #                     style=kpi_style,
    #                 ),
    #                 data_ba_dropdown(),
    #                 dcc.Graph(id="output-demand-time-line-graph"),
    #                 html.H1("Data Sources"),
    #                 html.P("EIA API https://www.eia.gov/opendata/"),
    #                 html.P(
    #                     "Weather API https://open-meteo.com/en/docs/historical-forecast-api"
    #                 ),
    #                 html.P(
    #                     "EIA 2025 Plant Data https://www.eia.gov/electricity/data/eia860/"
    #                 ),
    #                 html.P(
    #                     "Population Data https://www.census.gov/data/tables/time-series/demo/popest/2020s-total-cities-and-towns.html"
    #                 ),
    #                 html.P(
    #                     "Geo Data https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.2020.html#list-tab-264479560"
    #                 ),
    #                 html.P(
    #                     "BA Territory Data https://data.catalyst.coop/preview/pudl/out_eia861__yearly_balancing_authority_service_territory"
    #                 ),
    #                 html.P(
    #                     "Additional BA Territory Data https://www.eia.gov/electricity/data/eia861/"
    #                 ),
    #             ]
    #         )
    #     ],
    # )

    # pipeline_tab = dcc.Tab(
    #     label="Pipeline",
    #     style=tab_style,
    #     selected_style=tab_selected_style,
    #     children=[
    #         html.Section(
    #             [
    #                 html.H1("Pipeline"),
    #                 html.Section(
    #                     [
    #                         kpi_card(
    #                             "Last Completed",
    #                             value=render_latest_completion(),
    #                         ),
    #                         kpi_card("Next Run", value=get_next_run_time()),
    #                     ],
    #                     style=kpi_style,
    #                 ),
    #                 html.H1("Pipeline Diagram"),
    #                 html.Img(
    #                     src=app.get_asset_url("pipeline_diagram.png"),
    #                     style={"height": "200px", "width": "auto"},
    #                 ),
    #                 html.H1("ERD"),
    #                 html.Img(
    #                     src=app.get_asset_url("electricity_erd.png"),
    #                     style={"height": "200px", "width": "auto"},
    #                 ),
    #                 html.H1("Balancing Authority Weather Locations"),
    #                 dcc.Graph(figure=pipeline_ba_map()),
    #                 html.P(
    #                     """Balancing Authorities (BAs) can cover very large areas of the U.S.,
    #                     so are mapped to 3 specific locations determined and weighted by
    #                     population. Each location has a weather weight used to assign weather
    #                     values to that BA. For example: a BA with temperatures of (30, 28, 25)°F
    #                     and weights of (0.5, 0.3, 0.2) give (30°F x 0.5) + (28°F x 0.3) +
    #                     (25°F x 0.2) = 28.4°F for that BA."""
    #                 ),
    #             ]
    #         )
    #     ],
    # )
    grid_landscape_tab = dcc.Tab(label="Grid Landscape", disabled=True, style=tab_style)
    # national_pic_tab = dcc.Tab(
    #     label="National Picture",
    #     style=tab_style,
    #     selected_style=tab_selected_style,
    #     children=[
    #         html.Section(
    #             [
    #                 html.H1("National Picture"),
    #                 html.Section(
    #                     [
    #                         kpi_card("Most Recent Period", value=nat_pic_kpis()[0]),
    #                         kpi_card("Total Generation", value=nat_pic_kpis()[1]),
    #                         kpi_card("Total Demand", value=nat_pic_kpis()[2]),
    #                         kpi_card("Primary Energy Source", value=nat_pic_kpis()[3]),
    #                         kpi_card(
    #                             f"Generation from {nat_pic_kpis()[3]}",
    #                             value=nat_pic_kpis()[4],
    #                         ),
    #                     ],
    #                     style=kpi_style,
    #                 ),
    #                 dcc.Graph(figure=nat_pic_demand_line_graph()),
    #                 dcc.Graph(figure=nat_pic_fuel_graph()),
    #             ]
    #         )
    #     ],
    # )
    # ba_tab = dcc.Tab(
    #     label="Balancing Authorities",
    #     style=tab_style,
    #     selected_style=tab_selected_style,
    #     children=[
    #         html.Section(
    #             [
    #                 html.H1("Balancing Authorities"),
    #                 html.P(
    #                     """Balancing Authorities (BAs) are the organizations responsible for
    #                        keeping electric supply and demand in balance within its region. Each
    #                        BA forecasts demand for its region and directs the power plants within
    #                        it to generate the right amount of electricity.
    #                        """
    #                 ),
    #                 html.Section(
    #                     [
    #                         kpi_card(
    #                             "Cleanest BA", value_id="output-ba-kpi-metric-cleanest"
    #                         ),
    #                         kpi_card(
    #                             "Highest Avg Demand",
    #                             value_id="output-ba-kpi-metric-demand",
    #                         ),
    #                         kpi_card(
    #                             "Highest Avg Generation",
    #                             value_id="output-ba-kpi-metric-gen",
    #                         ),
    #                         kpi_card("Metric Top", value_id="output-ba-kpi-metric-top"),
    #                         kpi_card(
    #                             "Metric Bottom", value_id="output-ba-kpi-metric-bottom"
    #                         ),
    #                     ],
    #                     style=kpi_style,
    #                 ),
    #                 ba_metric_dropdown(),
    #                 dcc.Graph(id="output-ba-metric-map"),
    #                 dcc.Graph(id="output-ba-metric-bar"),
    #             ]
    #         )
    #     ],
    # )
    weather_tab = dcc.Tab(
        label="Weather",
        style=tab_style,
        selected_style=tab_selected_style,
        children=[
            html.Section(
                [
                    html.H1("Weather"),
                    html.P(
                        """Balance temperature looks at which temperature people use the least 
                        amount of energy. If the balance temperature falls at the edge of the graph
                        it is deemed invalid because there is no upward turn or 'U' shape.
                        """
                    ),
                    html.Section(
                        [
                            kpi_card(
                                "Average Temperature",
                                value_id="output-weather-kpi-temp",
                            ),
                            kpi_card(
                                "Balance Temperature",
                                value_id="output-weather-kpi-balance",
                            ),
                            kpi_card(
                                "Balance Demand",
                                value_id="output-weather-kpi-bal-demand",
                            ),
                            kpi_card(
                                "Average Demand",
                                value_id="output-weather-kpi-demand",
                            ),
                        ],
                        style=kpi_style,
                    ),
                    weather_ba_dropdown(),
                    dcc.Graph(id="output-weather-demand-scatter"),
                    dcc.Graph(id="output-weather-code-bar"),
                    dcc.Graph(id="output-weather-renewables-scatter"),
                ]
            )
        ],
    )

    layout = html.Div(
        dcc.Tabs(
            vertical=True,
            parent_style={"height": "calc(100vh - 100px)"},
            style={
                "flex": "0 0 200px",
                "width": "160px",
                "minWidth": "160px",
                "overflowY": "auto",
            },
            content_style={
                "flex": "1",
                "minWidth": "0",
                "minHeight": "0",
                "overflowY": "auto",
                "padding": "0 16px",
            },
            colors={"border": "#d6d6d6", "primary": "#1975FA", "background": "#f9f9f9"},
            children=[
                overview_tab,
                method_tab,
                # data_tab,
                # pipeline_tab,
                grid_landscape_tab,
                # national_pic_tab,
                # ba_tab,
                weather_tab,
            ],
        )
    )
    return layout
