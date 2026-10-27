import callbacks
from dash import dcc, html
from graphs import (
    nat_pic_demand_line_graph,
    nat_pic_fuel_graph,
    nat_pic_kpis,
    overview_ba_map,
    overview_temp_graph,
    pipeline_ba_map,
    pop_inc_demand_inc_scatter,
    pop_inc_demand_pop_scatter,
    pop_inc_kpis,
)
from init_app import app
from inputs import (
    ba_metric_dropdown,
    data_ba_dropdown,
    data_table_dropdown,
    weather_ba_dropdown,
)
from styles import (
    APP_STYLE,
    CARD_BODY_STYLE,
    CARD_TITLE_STYLE,
    CHART_CARD_STYLE,
    CHART_GRID_STYLE,
    COLORS,
    CONTENT_STYLE,
    DATA_CHART_STYLE,
    DATA_FILTER_ROW_STYLE,
    DATA_LINK_STYLE,
    DATA_RESOURCE_CARD_STYLE,
    DATA_TABLE_DETAILS_STYLE,
    DATA_TABLE_SUMMARY_STYLE,
    ERD_IMAGE_STYLE,
    FORMULA_BOX_STYLE,
    GRAPH_STYLE,
    INTRO_CARD_STYLE,
    KPI_CARD_STYLE,
    KPI_GRID_STYLE,
    KPI_LABEL_STYLE,
    OVERVIEW_ANSWER_STYLE,
    OVERVIEW_DETAILS_STYLE,
    OVERVIEW_DETAILS_SUMMARY_STYLE,
    OVERVIEW_KPI_GRID_STYLE,
    OVERVIEW_KPI_VALUE_STYLE,
    OVERVIEW_LINK_STYLE,
    OVERVIEW_QUESTION_CARD_STYLE,
    OVERVIEW_QUESTION_GRID_STYLE,
    OVERVIEW_VISUAL_CARD_STYLE,
    OVERVIEW_VISUAL_GRID_STYLE,
    PIPELINE_CARD_STYLE,
    PIPELINE_COLUMN_STYLE,
    PIPELINE_DIAGRAM_IMAGE_STYLE,
    PIPELINE_KPI_STYLE,
    PIPELINE_LAYOUT_STYLE,
    SIDEBAR_FOOTER_NAME_STYLE,
    SIDEBAR_FOOTER_STYLE,
    TAB_HEADER_STYLE,
    TAB_SELECTED_STYLE,
    TAB_STYLE,
    TABS_CONTENT_STYLE,
    TABS_PARENT_STYLE,
    TABS_STYLE,
    WEATHER_CONTROLS_STYLE,
    WEATHER_KPI_GRID_STYLE,
    WEATHER_LAYOUT_STYLE,
)
from tables import count_bas_covered, kpi_card

from data import (
    get_natural_gas_share,
    get_next_run_time,
    get_temp_balance_point,
    render_latest_completion,
)


def layout():
    QUESTIONS = False

    overview_header_tab = dcc.Tab(
        label="Overview",
        disabled=True,
        disabled_style=TAB_HEADER_STYLE,
    )

    overview_fuel_figure = nat_pic_fuel_graph()
    natural_gas_share = get_natural_gas_share(overview_fuel_figure)

    weather_kpi_values = callbacks.update_weather_kpis(None)
    balance_temp, balance_demand = get_temp_balance_point(weather_kpi_values)

    overview_temperature_figure = overview_temp_graph(
        callbacks.update_weather_demand_scatter(None),
        balance_temp,
    )
    overview_map_figure = overview_ba_map(callbacks.ba_metrics_df)

    def overview_question(title, answer, button_label, link_id):
        return html.Section(
            [
                html.H3(title, style=CARD_TITLE_STYLE),
                html.P(answer, style=OVERVIEW_ANSWER_STYLE),
                html.Button(
                    button_label,
                    id={"type": "overview-tab-link", "index": link_id},
                    n_clicks=0,
                    type="button",
                    style=OVERVIEW_LINK_STYLE,
                ),
            ],
            style=OVERVIEW_QUESTION_CARD_STYLE,
        )

    overview_tab = dcc.Tab(
        label="Overview",
        value="overview_tab",
        style=TAB_STYLE,
        selected_style=TAB_SELECTED_STYLE,
        children=[
            html.Div(
                [
                    html.Section(
                        [
                            html.H1("Overview"),
                            html.P("""
                                A data-driven analysis on U.S. electricity demand and generation, and how weather, 
                                geography, population, and income relate to energy use.
                                """),
                        ],
                        style=INTRO_CARD_STYLE,
                    ),
                    html.Section(
                        [
                            kpi_card(
                                "Balancing Authorities Covered",
                                value=count_bas_covered(),
                                card_style=KPI_CARD_STYLE,
                                label_style=KPI_LABEL_STYLE,
                                value_style=OVERVIEW_KPI_VALUE_STYLE,
                            ),
                            kpi_card(
                                "Natural Gas Share (Last 14 Days)",
                                value=natural_gas_share,
                                card_style=KPI_CARD_STYLE,
                                label_style=KPI_LABEL_STYLE,
                                value_style=OVERVIEW_KPI_VALUE_STYLE,
                            ),
                            kpi_card(
                                "Balance Temperature",
                                value=balance_temp,
                                card_style=KPI_CARD_STYLE,
                                label_style=KPI_LABEL_STYLE,
                                value_style=OVERVIEW_KPI_VALUE_STYLE,
                            ),
                            kpi_card(
                                "Demand at Balance Temperature",
                                value=balance_demand,
                                card_style=KPI_CARD_STYLE,
                                label_style=KPI_LABEL_STYLE,
                                value_style=OVERVIEW_KPI_VALUE_STYLE,
                            ),
                        ],
                        style=OVERVIEW_KPI_GRID_STYLE,
                    ),
                    html.Div(
                        [
                            html.Div(
                                dcc.Graph(
                                    figure=overview_map_figure,
                                    config={"responsive": True},
                                    style=GRAPH_STYLE,
                                ),
                                style=OVERVIEW_VISUAL_CARD_STYLE,
                            ),
                            html.Div(
                                dcc.Graph(
                                    figure=overview_temperature_figure,
                                    config={"responsive": True},
                                    style=GRAPH_STYLE,
                                ),
                                style=OVERVIEW_VISUAL_CARD_STYLE,
                            ),
                        ],
                        style=OVERVIEW_VISUAL_GRID_STYLE,
                    ),
                    html.Div(
                        [
                            overview_question(
                                "How does demand and generation vary by area?",
                                "Total demand and generation scale with BA size. Normalized demand is consistent across BAs, and most demand more than they generate.",
                                "Explore Balancing Authorities",
                                "ba-area",
                            ),
                            overview_question(
                                "How does weather affect demand and renewables?",
                                "Demand follows temperature and has an estimated balance point of 50°F. Wind and cloud conditions show slight correlation with renewable generation.",
                                "Explore Weather",
                                "weather-renewables",
                            ),
                            overview_question(
                                "Can weather help predict electricity use?",
                                "Demand varies with temperature, making forecasting useful. However, demand does not significantly vary with weather condition.",
                                "Explore Weather",
                                "weather-forecast",
                            ),
                            overview_question(
                                "Does population affect electricity use?",
                                "There is little relationship between BA population estimates and demand per person.",
                                "Explore Population & Income",
                                "population",
                            ),
                            overview_question(
                                "Do higher-income areas use more electricity?",
                                "There is little relationship between estimated income and demand per person.",
                                "Explore Population & Income",
                                "income",
                            ),
                        ],
                        style=OVERVIEW_QUESTION_GRID_STYLE,
                    ),
                    html.Details(
                        [
                            html.Summary(
                                "Definitions",
                                style=OVERVIEW_DETAILS_SUMMARY_STYLE,
                            ),
                            html.P(
                                """
                                Balancing Authorities (BAs) coordinate electricity supply and demand across their
                                service areas. Their areas can span large regions.
                                """,
                                style=CARD_BODY_STYLE,
                            ),
                            html.P(
                                """
                                Temperatures are in Fahrenheit. Demand, generation, and interchange are shown in
                                megawatt-hours (MWh). Database periods are stored in UTC/GMT and displayed in 
                                Central time where applicable.
                                """,
                                style=CARD_BODY_STYLE,
                            ),
                            html.P(
                                """
                                Mega-watt hour (MWh) is a unit of electric measurement. 1 MWh is a massive block 
                                of energy. With it, you can: power the average U.S. home for 1.2 months, drive an
                                electric car 3,600 miles (U.S. coast to coast), or run 2 refrigerators for a year.
                                """,
                                style=CARD_BODY_STYLE,
                            ),
                        ],
                        style=OVERVIEW_DETAILS_STYLE,
                    ),
                    html.Details(
                        [
                            html.Summary(
                                "Limitations",
                                style=OVERVIEW_DETAILS_SUMMARY_STYLE,
                            ),
                            html.P(
                                """
                                Weather is mapped to representative locations for each BA, so it cannot capture
                                every local condition. The map includes only authorities with usable demand, 
                                generation, and location metrics.
                                """,
                                style=CARD_BODY_STYLE,
                            ),
                            html.P(
                                """
                                The analysis covers a limited historical window and U.S. electricity data. 
                                Aggregated BA-level comparisons can hide differences among individual plants 
                                and communities.
                                """,
                                style=CARD_BODY_STYLE,
                            ),
                        ],
                        style=OVERVIEW_DETAILS_STYLE,
                    ),
                    html.Details(
                        [
                            html.Summary(
                                "Next Steps",
                                style=OVERVIEW_DETAILS_SUMMARY_STYLE,
                            ),
                            html.Ul(
                                [
                                    html.Li(
                                        "Analyze precipitation, rain, snow, and UV in relation to renewable generation."
                                    ),
                                    html.Li(
                                        "Build a temperature-based demand prediction model and see how well of a predictor it really is."
                                    ),
                                    html.Li(
                                        "Expand coverage and compare electricity use and generation across more regions."
                                    ),
                                ],
                                style={**CARD_BODY_STYLE, "paddingLeft": "22px"},
                            ),
                        ],
                        style=OVERVIEW_DETAILS_STYLE,
                    ),
                ],
                style=CONTENT_STYLE,
            )
        ],
    )

    method_tab = dcc.Tab(
        label="Methodology", disabled=True, disabled_style=TAB_HEADER_STYLE
    )

    data_tab = dcc.Tab(
        label="Data",
        value="data_tab",
        style=TAB_STYLE,
        selected_style=TAB_SELECTED_STYLE,
        children=[
            html.Div(
                [
                    html.Section(
                        [
                            html.H1("Data"),
                            html.P("""
                                View overarching electricity demand and temperature coverage 
                                across the BAs included in this project.
                                """),
                        ],
                        style=INTRO_CARD_STYLE,
                    ),
                    html.Section(
                        [
                            kpi_card(
                                "Balancing Authorities Covered",
                                value=count_bas_covered(),
                                card_style=KPI_CARD_STYLE,
                                label_style=KPI_LABEL_STYLE,
                            ),
                            kpi_card(
                                "Date Ranges Covered",
                                value_id="output-data-kpi-date-range",
                                card_style=KPI_CARD_STYLE,
                                label_style=KPI_LABEL_STYLE,
                            ),
                            kpi_card(
                                "Total Aggregate Demand",
                                value_id="output-data-kpi-total-mwh",
                                card_style=KPI_CARD_STYLE,
                                label_style=KPI_LABEL_STYLE,
                            ),
                        ],
                        style=KPI_GRID_STYLE,
                    ),
                    html.Section(
                        [
                            html.Div(
                                data_ba_dropdown(),
                                style=DATA_FILTER_ROW_STYLE,
                            ),
                            dcc.Graph(
                                id="output-demand-time-line-graph",
                                config={"responsive": True},
                                style=GRAPH_STYLE,
                            ),
                        ],
                        style=DATA_CHART_STYLE,
                    ),
                    html.Details(
                        [
                            html.Summary(
                                "Explore Table Previews",
                                style=DATA_TABLE_SUMMARY_STYLE,
                            ),
                            html.Div(
                                data_table_dropdown(),
                                style={
                                    "width": "100%",
                                    "marginBottom": "14px",
                                    "marginTop": "14px",
                                },
                            ),
                            html.Div(
                                id="output-data-table-preview",
                                style={"width": "100%"},
                            ),
                        ],
                        style=DATA_TABLE_DETAILS_STYLE,
                    ),
                    html.Section(
                        [
                            html.P(
                                "Data sources are documented in the project README.",
                                style={"margin": "0"},
                            ),
                            html.A(
                                "View Database Schema",
                                href="https://github.com/JackRWilson/Capstone/blob/main/db/electricity_schema.sql",
                                target="_blank",
                                rel="noreferrer",
                                style=DATA_LINK_STYLE,
                            ),
                        ],
                        style=DATA_RESOURCE_CARD_STYLE,
                    ),
                ],
                style=CONTENT_STYLE,
            )
        ],
    )

    pipeline_tab = dcc.Tab(
        label="Pipeline",
        value="pipeline_tab",
        style=TAB_STYLE,
        selected_style=TAB_SELECTED_STYLE,
        children=[
            html.Div(
                [
                    html.Section(
                        [
                            html.H1("Pipeline"),
                            html.P("""
                                Track recent and upcoming pipeline runs, explore the schema,
                                processing flow, and how BA weather locations are weighted.
                                """),
                        ],
                        style=INTRO_CARD_STYLE,
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    kpi_card(
                                        "Last Completed Run",
                                        value=render_latest_completion(),
                                        card_style=PIPELINE_KPI_STYLE,
                                        label_style=KPI_LABEL_STYLE,
                                    ),
                                    kpi_card(
                                        "Next Scheduled Run",
                                        value=get_next_run_time(),
                                        card_style=PIPELINE_KPI_STYLE,
                                        label_style=KPI_LABEL_STYLE,
                                    ),
                                    html.Div(
                                        [
                                            html.H3(
                                                "Entity Relationship Diagram",
                                                style=CARD_TITLE_STYLE,
                                            ),
                                            html.Img(
                                                src=app.get_asset_url(
                                                    "electricity_erd.png"
                                                ),
                                                style=ERD_IMAGE_STYLE,
                                            ),
                                        ],
                                        style={**PIPELINE_CARD_STYLE, "flex": "1"},
                                    ),
                                ],
                                style=PIPELINE_COLUMN_STYLE,
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H3(
                                                "Pipeline Diagram",
                                                style=CARD_TITLE_STYLE,
                                            ),
                                            html.Img(
                                                src=app.get_asset_url(
                                                    "pipeline_diagram.png"
                                                ),
                                                style=PIPELINE_DIAGRAM_IMAGE_STYLE,
                                            ),
                                        ],
                                        style={
                                            **PIPELINE_CARD_STYLE,
                                            "flex": "0 0 auto",
                                        },
                                    ),
                                    html.Div(
                                        [
                                            html.H3(
                                                "Balancing Authority Location Weight (e.g. Associated Electric Cooperative, Inc. - AECI)",
                                                style=CARD_TITLE_STYLE,
                                            ),
                                            html.P(
                                                """
                                                Each BA has 3 locations mapped to it by the top 3 most populated counties
                                                in its region.
                                                Each location within the BA has a weight:
                                                """,
                                                style=CARD_BODY_STYLE,
                                            ),
                                            html.P(
                                                """
                                                Weight = Location Population / Total Population of all 3 locations
                                                """,
                                                style=FORMULA_BOX_STYLE,
                                            ),
                                            html.P(
                                                """
                                                Weather variables are mapped to the BA using this weight:
                                                """,
                                                style=CARD_BODY_STYLE,
                                            ),
                                            html.P(
                                                """
                                                AECI Temperature = (74.3°F x 33.8%) + (83.5°F x 30.2%) + (79.1°F x 36.0%) = 78.8°F
                                                """,
                                                style=FORMULA_BOX_STYLE,
                                            ),
                                            dcc.Graph(
                                                figure=pipeline_ba_map(),
                                                config={"responsive": True},
                                                style={
                                                    **GRAPH_STYLE,
                                                    "flex": "1",
                                                    "minHeight": 0,
                                                },
                                            ),
                                        ],
                                        style={**PIPELINE_CARD_STYLE, "flex": "1"},
                                    ),
                                ],
                                style=PIPELINE_COLUMN_STYLE,
                            ),
                        ],
                        style=PIPELINE_LAYOUT_STYLE,
                    ),
                ],
                style=CONTENT_STYLE,
            ),
        ],
    )

    grid_landscape_tab = dcc.Tab(
        label="Grid Landscape", disabled=True, disabled_style=TAB_HEADER_STYLE
    )

    national_kpi_values = nat_pic_kpis()
    national_pic_tab = dcc.Tab(
        label="National Picture",
        value="national_pic_tab",
        style=TAB_STYLE,
        selected_style=TAB_SELECTED_STYLE,
        children=[
            html.Div(
                [
                    html.Section(
                        [
                            html.H1("National Picture"),
                            html.P("""
                                Compare recent U.S. electricity demand with generation by fuel source.
                                This data uses periods with complete BA coverage.
                                """),
                        ],
                        style=INTRO_CARD_STYLE,
                    ),
                    html.Section(
                        [
                            kpi_card(
                                "Most Recent Complete Period",
                                value=national_kpi_values[0],
                                card_style=KPI_CARD_STYLE,
                                label_style=KPI_LABEL_STYLE,
                            ),
                            kpi_card(
                                "Period Generation",
                                value=national_kpi_values[1],
                                card_style=KPI_CARD_STYLE,
                                label_style=KPI_LABEL_STYLE,
                            ),
                            kpi_card(
                                "Period Demand",
                                value=national_kpi_values[2],
                                card_style=KPI_CARD_STYLE,
                                label_style=KPI_LABEL_STYLE,
                            ),
                            kpi_card(
                                "Primary Energy Source",
                                value=national_kpi_values[3],
                                card_style=KPI_CARD_STYLE,
                                label_style=KPI_LABEL_STYLE,
                            ),
                            kpi_card(
                                f"Generation from {national_kpi_values[3]}",
                                value=national_kpi_values[4],
                                card_style=KPI_CARD_STYLE,
                                label_style=KPI_LABEL_STYLE,
                            ),
                        ],
                        style=KPI_GRID_STYLE,
                    ),
                    html.Div(
                        [
                            html.Div(
                                dcc.Graph(
                                    figure=nat_pic_demand_line_graph(),
                                    config={"responsive": True},
                                    style=GRAPH_STYLE,
                                ),
                                style=CHART_CARD_STYLE,
                            ),
                            html.Div(
                                dcc.Graph(
                                    figure=overview_fuel_figure,
                                    config={"responsive": True},
                                    style=GRAPH_STYLE,
                                ),
                                style=CHART_CARD_STYLE,
                            ),
                        ],
                        style=CHART_GRID_STYLE,
                    ),
                ],
                style=CONTENT_STYLE,
            )
        ],
    )

    ba_tab = dcc.Tab(
        label="Balancing Authorities",
        value="ba_tab",
        style=TAB_STYLE,
        selected_style=TAB_SELECTED_STYLE,
        children=[
            html.Div(
                [
                    html.Section(
                        [
                            html.H1("Balancing Authorities"),
                            html.P("""
                                Compare how BAs stack up against each other using metrics such
                                as average demand, peak-to-average demand (normalized demand metric), 
                                renewable generation percentage, and interchange percent (0% = 
                                generate as much as demand, 100% = only generation).
                                """),
                            html.P("""
                                Q1: How does demand and generation vary by area?
                                """) if QUESTIONS else None,
                        ],
                        style=INTRO_CARD_STYLE,
                    ),
                    html.Section(
                        [
                            kpi_card(
                                "Cleanest BA",
                                value_id="output-ba-kpi-metric-cleanest",
                                card_style=KPI_CARD_STYLE,
                                label_style=KPI_LABEL_STYLE,
                            ),
                            kpi_card(
                                "Highest Avg Demand",
                                value_id="output-ba-kpi-metric-demand",
                                card_style=KPI_CARD_STYLE,
                                label_style=KPI_LABEL_STYLE,
                            ),
                            kpi_card(
                                "Highest Avg Generation",
                                value_id="output-ba-kpi-metric-gen",
                                card_style=KPI_CARD_STYLE,
                                label_style=KPI_LABEL_STYLE,
                            ),
                            kpi_card(
                                "Metric Top",
                                value_id="output-ba-kpi-metric-top",
                                card_style=KPI_CARD_STYLE,
                                label_style=KPI_LABEL_STYLE,
                            ),
                            kpi_card(
                                "Metric Bottom",
                                value_id="output-ba-kpi-metric-bottom",
                                card_style=KPI_CARD_STYLE,
                                label_style=KPI_LABEL_STYLE,
                            ),
                        ],
                        style=KPI_GRID_STYLE,
                    ),
                    html.Div(
                        ba_metric_dropdown(),
                    ),
                    html.Div(
                        [
                            html.Div(
                                dcc.Graph(
                                    id="output-ba-metric-map",
                                    config={"responsive": True},
                                    style=GRAPH_STYLE,
                                ),
                                style=CHART_CARD_STYLE,
                            ),
                            html.Div(
                                dcc.Graph(
                                    id="output-ba-metric-bar",
                                    config={"responsive": True},
                                    style=GRAPH_STYLE,
                                ),
                                style=CHART_CARD_STYLE,
                            ),
                        ],
                        style=CHART_GRID_STYLE,
                    ),
                ],
                style=CONTENT_STYLE,
            )
        ],
    )

    weather_tab = dcc.Tab(
        label="Weather",
        value="weather_tab",
        style=TAB_STYLE,
        selected_style=TAB_SELECTED_STYLE,
        children=[
            html.Div(
                [
                    html.Section(
                        [
                            html.H1("Weather"),
                            html.P("""
                                Explore how temperature and weather conditions relate to
                                electricity demand and renewable generation. Balance temperature
                                is the temperature associated with the lowest demand. Values
                                at the edge of the observed range are omitted because a minimum
                                cannot reliably be identified.
                                """),
                            html.P("""
                                Q2 & 3: How does weather affect demand, generation, and renewables? Can weather help predict electricity use?
                                """) if QUESTIONS else None,
                        ],
                        style=INTRO_CARD_STYLE,
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    weather_ba_dropdown(),
                                    html.Section(
                                        [
                                            kpi_card(
                                                "Average Temperature",
                                                value_id="output-weather-kpi-temp",
                                                card_style=KPI_CARD_STYLE,
                                                label_style=KPI_LABEL_STYLE,
                                            ),
                                            kpi_card(
                                                "Balance Temperature",
                                                value_id="output-weather-kpi-balance",
                                                card_style=KPI_CARD_STYLE,
                                                label_style=KPI_LABEL_STYLE,
                                            ),
                                            kpi_card(
                                                "Demand at Balance Temperature",
                                                value_id="output-weather-kpi-bal-demand",
                                                card_style=KPI_CARD_STYLE,
                                                label_style=KPI_LABEL_STYLE,
                                            ),
                                            kpi_card(
                                                "Average Demand",
                                                value_id="output-weather-kpi-demand",
                                                card_style=KPI_CARD_STYLE,
                                                label_style=KPI_LABEL_STYLE,
                                            ),
                                        ],
                                        style=WEATHER_KPI_GRID_STYLE,
                                    ),
                                ],
                                style=WEATHER_CONTROLS_STYLE,
                            ),
                            html.Div(
                                dcc.Graph(
                                    id="output-weather-demand-scatter",
                                    config={"responsive": True},
                                    style=GRAPH_STYLE,
                                ),
                                style={**CHART_CARD_STYLE, "gridArea": "demand"},
                            ),
                            html.Div(
                                dcc.Graph(
                                    id="output-weather-code-bar",
                                    config={"responsive": True},
                                    style=GRAPH_STYLE,
                                ),
                                style={**CHART_CARD_STYLE, "gridArea": "code"},
                            ),
                            html.Div(
                                dcc.Graph(
                                    id="output-weather-wind-scatter",
                                    config={"responsive": True},
                                    style=GRAPH_STYLE,
                                ),
                                style={**CHART_CARD_STYLE, "gridArea": "wind"},
                            ),
                            html.Div(
                                dcc.Graph(
                                    id="output-weather-solar-scatter",
                                    config={"responsive": True},
                                    style=GRAPH_STYLE,
                                ),
                                style={**CHART_CARD_STYLE, "gridArea": "solar"},
                            ),
                        ],
                        style=WEATHER_LAYOUT_STYLE,
                    ),
                ],
                style=CONTENT_STYLE,
            )
        ],
    )

    pop_inc_kpi_values = pop_inc_kpis()
    pop_income_tab = dcc.Tab(
        label="Population & Income",
        value="pop_income_tab",
        style=TAB_STYLE,
        selected_style=TAB_SELECTED_STYLE,
        children=[
            html.Div(
                [
                    html.Section(
                        [
                            html.H1("Population & Income"),
                            html.P("""
                                Compare average hourly electricity demand per person (kW/person) across
                                BAs against county population and per capita income.
                                """),
                            html.P("""
                                Q 4 & 5: Does population affect electricity use? Do higher income areas use more electricity?
                                """) if QUESTIONS else None,
                        ],
                        style=INTRO_CARD_STYLE,
                    ),
                    html.Section(
                        [
                            kpi_card(
                                "Population R²",
                                value=pop_inc_kpi_values[1],
                                card_style=KPI_CARD_STYLE,
                                label_style=KPI_LABEL_STYLE,
                            ),
                            kpi_card(
                                "Demand Change per +100,000 Population",
                                value=pop_inc_kpi_values[3],
                                card_style=KPI_CARD_STYLE,
                                label_style=KPI_LABEL_STYLE,
                            ),
                            kpi_card(
                                "Income R²",
                                value=pop_inc_kpi_values[0],
                                card_style=KPI_CARD_STYLE,
                                label_style=KPI_LABEL_STYLE,
                            ),
                            kpi_card(
                                "Demand Change per +$10,000 Income",
                                value=pop_inc_kpi_values[2],
                                card_style=KPI_CARD_STYLE,
                                label_style=KPI_LABEL_STYLE,
                            ),
                        ],
                        style=KPI_GRID_STYLE,
                    ),
                    html.Div(
                        [
                            html.Div(
                                dcc.Graph(
                                    figure=pop_inc_demand_pop_scatter(),
                                    config={"responsive": True},
                                    style=GRAPH_STYLE,
                                ),
                                style=CHART_CARD_STYLE,
                            ),
                            html.Div(
                                dcc.Graph(
                                    figure=pop_inc_demand_inc_scatter(),
                                    config={"responsive": True},
                                    style=GRAPH_STYLE,
                                ),
                                style=CHART_CARD_STYLE,
                            ),
                        ],
                        style=CHART_GRID_STYLE,
                    ),
                ],
                style=CONTENT_STYLE,
            )
        ],
    )

    layout = html.Div(
        [
            dcc.Tabs(
                id="app-tabs",
                vertical=True,
                value="overview_tab",
                parent_style=TABS_PARENT_STYLE,
                style=TABS_STYLE,
                content_style=TABS_CONTENT_STYLE,
                colors={
                    "border": COLORS["border"],
                    "primary": COLORS["accent"],
                    "background": COLORS["page"],
                },
                children=[
                    overview_header_tab,
                    overview_tab,
                    method_tab,
                    data_tab,
                    pipeline_tab,
                    grid_landscape_tab,
                    national_pic_tab,
                    ba_tab,
                    weather_tab,
                    pop_income_tab,
                ],
            ),
            html.Div(
                [
                    html.P("Jack Wilson", style=SIDEBAR_FOOTER_NAME_STYLE),
                    html.A(
                        "GitHub Repository",
                        href="https://github.com/JackRWilson/Capstone",
                        target="_blank",
                        rel="noreferrer",
                        style={**DATA_LINK_STYLE, "fontSize": "14px"},
                    ),
                ],
                style=SIDEBAR_FOOTER_STYLE,
            ),
        ],
        style=APP_STYLE,
    )
    return layout
