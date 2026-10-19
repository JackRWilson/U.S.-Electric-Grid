import callbacks  # noqa: F401
from dash import dcc, html
from inputs import data_ba_dropdown
from tables import count_bas_covered, kpi_card, render_grid, render_table

overview_tab = dcc.Tab(
    label="Overview",
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
method_tab = dcc.Tab(label="Methodology", disabled=True)
data_tab = dcc.Tab(
    label="Data",
    children=[
        html.Section(
            [
                html.H1("Data"),
                html.P(
                    "Seven different data sources are combined to create a comprehensive electricity, county, income, and population dataset. The final schema consists of 9 relational tables."
                ),
                html.H1("Tables"),
                render_grid(
                    [
                        render_table(
                            table="Demand",
                            db_table="electric_demand",
                            order_by="period",
                            api_name="demand",
                        ),
                        render_table(
                            table="Generation",
                            db_table="electric_generation",
                            order_by="period",
                            api_name="generation",
                        ),
                        render_table(
                            table="Weather",
                            db_table="weather",
                            order_by="period",
                            api_name="weather",
                        ),
                        render_table(
                            table="County",
                            db_table="county",
                        ),
                        render_table(
                            table="Balancing Authority",
                            db_table="balancing_authority",
                        ),
                        render_table(
                            table="Fuel Type",
                            db_table="fuel_type",
                        ),
                        render_table(
                            table="Weather Location",
                            db_table="weather_location",
                        ),
                        render_table(
                            table="BA Weather Location",
                            db_table="ba_weather_location",
                        ),
                        render_table(
                            table="BA County",
                            db_table="ba_county",
                        ),
                    ]
                ),
                html.Section(
                    [
                        kpi_card("BAs Covered", value=count_bas_covered()),
                        kpi_card("Date Range", value_id="output-data-kpi-date-range"),
                        kpi_card("Total Demand", value_id="output-data-kpi-total-mwh"),
                    ],
                    style={"display": "flex", "gap": "16px", "marginBottom": "16px"},
                ),
                data_ba_dropdown(),
                dcc.Graph(id="output-demand-time-line-graph"),
                html.H1("Data Sources"),
                html.P("EIA API https://www.eia.gov/opendata/"),
                html.P(
                    "Weather API https://open-meteo.com/en/docs/historical-forecast-api"
                ),
                html.P(
                    "EIA 2025 Plant Data https://www.eia.gov/electricity/data/eia860/"
                ),
                html.P(
                    "Population Data https://www.census.gov/data/tables/time-series/demo/popest/2020s-total-cities-and-towns.html"
                ),
                html.P(
                    "Geo Data https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.2020.html#list-tab-264479560"
                ),
                html.P(
                    "BA Territory Data https://data.catalyst.coop/preview/pudl/out_eia861__yearly_balancing_authority_service_territory"
                ),
                html.P(
                    "Additional BA Territory Data https://www.eia.gov/electricity/data/eia861/"
                ),
            ]
        )
    ],
)

layout = html.Div(
    [html.Div([dcc.Tabs(vertical=True, children=[overview_tab, method_tab, data_tab])])]
)
