import pandas as pd

from dash import dash_table, html

from data import extract_data

data_table_settings = {
    "page_size": 3,
    "sort_action": "native",
    "style_table": {"overflowX": "auto"},
    "style_cell": {
        "minWidth": "160px",
        "width": "160px",
        "maxWidth": "160px",
        "overflow": "hidden",
        "textOverflow": "ellipsis",
        "whiteSpace": "nowrap",
        "fontFamily": "Helvetica",
        "fontSize": "14px",
    },
    "style_header": {
        "backgroundColor": "#BDBDBD",
        "fontWeight": "bold",
        "fontFamily": "Helvetica",
        "fontSize": "15px",
        "whiteSpace": "normal",
        "height": "auto",
        "overflow": "visible",
        "textOverflow": "clip",
    },
    "style_data_conditional": [
        {
            "if": {"row_index": "odd"},
            "backgroundColor": "#D3D3D3",
        },
        {
            "if": {"row_index": "even"},
            "backgroundColor": "white",
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
    info = f" - Rows: {length:,}"

    if api_name:
        last_update = extract_data(
            f"select last_period from electricity.etl_watermark where source = '{api_name}'"
        )
        if not last_update.empty:
            last_update = pd.to_datetime(last_update.iloc[0, 0]).strftime(
                "%Y/%m/%d %I:%M%p"
            )
            info = f" - Last update: {last_update}" + info
    return html.Section(
        [
            html.Div(
                [
                    html.H3(f"{table} Table", style={"margin": "0"}),
                    html.P(
                        info,
                        style={"margin": "0", "marginLeft": "8px"},
                    ),
                ],
                style={"display": "flex", "alignItems": "baseline"},
            ),
            dash_table.DataTable(data=df.to_dict("records"), **data_table_settings),
        ],
        style={"minWidth": "0"},
    )


def render_grid(sections):
    return html.Section(
        sections,
        style={
            "display": "grid",
            "gridTemplateColumns": "repeat(3, minmax(0, 1fr))",
            "gap": "24px",
            "padding": "16px",
        },
    )


def kpi_card(label, value_id=None, value="-"):
    value_info = {"style": {"margin": "4px 0 0 0"}}
    if value_id:
        value_info["id"] = value_id

    return html.Section(
        [
            html.P(
                label, style={"margin": "0", "fontSize": "13px", "color": "#616161"}
            ),
            html.H2(value, **value_info),
        ],
        style={
            "flex": "1",
            "padding": "12px 16px",
            "backgroundColor": "#F5F5F5",
            "borderRadius": "6px",
            "fontFamily": "Helvetica",
        },
    )


def count_bas_covered():
    sql = "select count(distinct ba_code) from balancing_authority"
    return int(extract_data(sql).iloc[0, 0])
