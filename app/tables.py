import pandas as pd
from dash import dash_table, html
from styles import CARD_STYLE, COLORS, DATA_TABLE_HEADER_STYLE, FONTS

from data import extract_data

DATA_TABLES = {
    "electric_demand": {
        "table": "Demand",
        "db_table": "electric_demand",
        "order_by": "period",
        "api_name": "demand",
    },
    "electric_generation": {
        "table": "Generation",
        "db_table": "electric_generation",
        "order_by": "period",
        "api_name": "generation",
    },
    "weather": {
        "table": "Weather",
        "db_table": "weather",
        "order_by": "period",
        "api_name": "weather",
    },
    "county": {
        "table": "County",
        "db_table": "county",
    },
    "balancing_authority": {
        "table": "Balancing Authority",
        "db_table": "balancing_authority",
    },
    "fuel_type": {
        "table": "Fuel Type",
        "db_table": "fuel_type",
    },
    "weather_location": {
        "table": "Weather Location",
        "db_table": "weather_location",
    },
    "ba_weather_location": {
        "table": "BA Weather Location",
        "db_table": "ba_weather_location",
    },
    "ba_county": {
        "table": "BA County",
        "db_table": "ba_county",
    },
}

data_table_settings = {
    "page_size": 5,
    "sort_action": "native",
    "style_table": {
        "width": "100%",
        "overflowX": "auto",
        "border": f"1px solid {COLORS['border']}",
        "borderRadius": "6px",
    },
    "style_cell": {
        "minWidth": "160px",
        "width": "160px",
        "maxWidth": "160px",
        "overflow": "hidden",
        "textOverflow": "ellipsis",
        "whiteSpace": "nowrap",
        "fontFamily": FONTS["mono"],
        "fontSize": "14px",
        "padding": "8px",
        "textAlign": "left",
        "border": f"1px solid {COLORS['border']}",
    },
    "style_data": {
        "backgroundColor": COLORS["surface"],
        "color": COLORS["text"],
    },
    "style_header": {
        "backgroundColor": COLORS["surface_hover"],
        "color": COLORS["text_strong"],
        "fontWeight": "bold",
        "fontFamily": FONTS["mono"],
        "fontSize": "14px",
        "whiteSpace": "normal",
        "height": "auto",
        "overflow": "visible",
        "textOverflow": "clip",
    },
    "style_data_conditional": [
        {
            "if": {"row_index": "odd"},
            "backgroundColor": "#2A2A2B",
        },
        {
            "if": {"row_index": "even"},
            "backgroundColor": COLORS["surface"],
        },
    ],
    "style_as_list_view": True,
    "css": [
        {
            "selector": ".dash-spreadsheet-container",
            "rule": f"background-color: {COLORS['surface']};",
        },
        {
            "selector": ".dash-spreadsheet td div",
            "rule": f"color: {COLORS['text']};",
        },
    ],
}


def render_table(table, db_table, order_by=None, api_name=None):
    sql = f"select count(*) from {db_table}"
    length = int(extract_data(sql).iloc[0, 0])

    sql = f"select * from {db_table}"
    if order_by:
        sql += f" order by {order_by} desc"
    sql += " limit 20"

    df = extract_data(sql)

    info_rows = f"Rows: {length:,}"
    info_update = ""
    if api_name:
        last_update = extract_data(
            f"select last_period from electricity.etl_watermark where source = '{api_name}'"
        )
        if not last_update.empty:
            last_update = pd.to_datetime(last_update.iloc[0, 0]).strftime(
                "%Y/%m/%d %I:%M%p"
            )
            info_update = f"Last update (UTC): {last_update}"
            if table == "Weather":
                info_update = f"Last update (GMT): {last_update}"

    return html.Section(
        [
            html.Div(
                [
                    html.H3(
                        f"{table} Table",
                        style={**DATA_TABLE_HEADER_STYLE, "textAlign": "left"},
                    ),
                    html.P(
                        info_update,
                        style={**DATA_TABLE_HEADER_STYLE, "textAlign": "center"},
                    ),
                    html.P(
                        info_rows,
                        style={**DATA_TABLE_HEADER_STYLE, "textAlign": "right"},
                    ),
                ],
                style={
                    "display": "flex",
                    "alignItems": "baseline",
                    "width": "100%",
                },
            ),
            dash_table.DataTable(data=df.to_dict("records"), **data_table_settings),
        ],
        style={
            **CARD_STYLE,
            "minWidth": "0",
            "padding": "12px",
        },
    )


def kpi_card(
    label,
    value_id=None,
    value="-",
    card_style=None,
    label_style=None,
    value_style=None,
):
    value_component_style = {"margin": "4px 0 0 0"}
    if value_style:
        value_component_style.update(value_style)
    value_info = {"style": value_component_style}
    if value_id:
        value_info["id"] = value_id

    label_component_style = {
        "margin": "0",
        "fontSize": "13px",
        "color": "#616161",
    }
    if label_style:
        label_component_style.update(label_style)

    card_component_style = {
        "flex": "1",
        "padding": "12px 16px",
        "backgroundColor": "#F5F5F5",
        "borderRadius": "6px",
        "fontFamily": "Helvetica",
    }
    if card_style:
        card_component_style.update(card_style)

    return html.Section(
        [
            html.P(label, style=label_component_style),
            html.H2(value, **value_info),
        ],
        style=card_component_style,
    )


def count_bas_covered():
    sql = "select count(distinct ba_code) from balancing_authority"
    return int(extract_data(sql).iloc[0, 0])
