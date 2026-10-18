from dash import html, dcc

test_tab = dcc.Tab(
    label="Overview",
    children=[
        html.Section(
            [
                html.Br(),
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

layout = html.Div([html.Div([dcc.Tabs(vertical=True, children=[test_tab])])])
