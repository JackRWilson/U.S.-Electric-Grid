# Design
COLORS = {
    "page": "#1E1E1E",
    "surface": "#252526",
    "surface_hover": "#2D2D30",
    "border": "#3C3C3C",
    "border_strong": "#555555",
    "text": "#D4D4D4",
    "text_strong": "#F3F3F3",
    "text_muted": "#B8C0CC",
    "text_subtle": "#9DA5B4",
    "accent": "#3794FF",
    "accent_light": "#75BEFF",
}

DATA_COLORS = {
    "blue": "#3794FF",
    "green": "#30D158",
    "orange": "#FF7A00",
    "blue_band": "rgba(55, 148, 255, 0.2)",
}

FONTS = {
    "ui": "Segoe UI, sans-serif",
    "mono": "Consolas, 'Courier New', monospace",
}

# --------------------------------------------------
# Shared blocks
FILL = {
    "width": "100%",
    "height": "100%",
    "minWidth": "0",
    "minHeight": "0",
}

CARD_STYLE = {
    "backgroundColor": COLORS["surface"],
    "border": f"1px solid {COLORS['border']}",
    "borderRadius": "8px",
}

# --------------------------------------------------
# Whole dashboard
APP_STYLE = {
    "width": "100vw",
    "height": "100vh",
    "minHeight": "100vh",
    "minWidth": "0",
    "margin": "0",
    "overflow": "hidden",
    "position": "relative",
    "backgroundColor": COLORS["page"],
    "color": COLORS["text"],
    "fontFamily": FONTS["ui"],
}

# --------------------------------------------------
# Tabs
TAB_STYLE = {
    "flex": "0 0 auto",
    "height": "34px",
    "minHeight": "0",
    "lineHeight": "34px",
    "padding": "0 12px",
    "fontSize": "14px",
    "whiteSpace": "nowrap",
    "overflow": "hidden",
    "textOverflow": "ellipsis",
    "textAlign": "left",
    "alignItems": "left",
    "backgroundColor": COLORS["surface"],
    "color": COLORS["text"],
    "fontFamily": FONTS["mono"],
    "borderLeft": "4px solid transparent",
}

TAB_SELECTED_STYLE = {
    **TAB_STYLE,
    "backgroundColor": COLORS["surface_hover"],
    "color": COLORS["text_strong"],
    "borderLeft": f"4px solid {COLORS['accent']}",
}

# Sidebar
TABS_STYLE = {
    "flex": "0 0 200px",
    "width": "200px",
    "minWidth": "200px",
    "height": "calc(100vh - 40px)",
    "overflowY": "auto",
    "boxSizing": "border-box",
    "backgroundColor": COLORS["surface"],
    "border": f"1px solid {COLORS['border']}",
    "borderRadius": "8px",
    "paddingBottom": "90px",
    "marginBottom": "20px",
    "marginTop": "20px",
    "marginLeft": "14px",
}

TABS_PARENT_STYLE = {
    **FILL,
    "display": "flex",
    "overflow": "hidden",
    "backgroundColor": COLORS["page"],
}

TABS_CONTENT_STYLE = {
    "display": "flex",
    "flex": "1",
    "height": "100%",
    "minWidth": "0",
    "minHeight": "0",
    "overflowY": "auto",
    "padding": "0",
    "backgroundColor": COLORS["page"],
}

TAB_HEADER_STYLE = {
    **TAB_STYLE,
    "color": COLORS["text_muted"],
    "textTransform": "uppercase",
    "cursor": "default",
    "pointerEvents": "none",
    "display": "flex",
    "flexDirection": "column",
    "height": "68px",
    "justifyContent": "flex-end",
    "fontSize": "15px",
}

SIDEBAR_FOOTER_STYLE = {
    "position": "absolute",
    "left": "30px",
    "bottom": "30px",
    "display": "flex",
    "flexDirection": "column",
    "gap": "5px",
    "zIndex": "1",
}

SIDEBAR_FOOTER_NAME_STYLE = {
    "margin": "0",
    "color": COLORS["text_muted"],
    "fontFamily": FONTS["mono"],
    "fontSize": "14px",
}

# --------------------------------------------------
# Page
CONTENT_STYLE = {
    "boxSizing": "border-box",
    "display": "flex",
    "flexDirection": "column",
    "width": "100%",
    "height": "100%",
    "minWidth": "0",
    "minHeight": "0",
    "padding": "20px",
    "gap": "14px",
    "overflowY": "auto",
    "backgroundColor": COLORS["page"],
    "color": COLORS["text"],
    "fontFamily": FONTS["ui"],
}

# --------------------------------------------------
# Inputs

DROPDOWN_STYLE = {
    "fontFamily": FONTS["mono"],
    "fontSize": "13px",
    "color": COLORS["text"],
    "width": "250px",
}

# --------------------------------------------------
# Cards

# Intro/desc
INTRO_CARD_STYLE = {
    **CARD_STYLE,
    "flex": "0 0 auto",
    "padding": "10px 10px",
    "fontFamily": FONTS["ui"],
}

# KPIs and label
KPI_CARD_STYLE = {
    **CARD_STYLE,
    "fontFamily": FONTS["mono"],
}

KPI_LABEL_STYLE = {"color": COLORS["text_subtle"]}

# Chart
CHART_CARD_STYLE = {
    **CARD_STYLE,
    "display": "flex",
    "flexDirection": "column",
    "minWidth": "0",
    "minHeight": "0",
    "overflow": "hidden",
    "padding": "14px",
}

CARD_TITLE_STYLE = {
    "color": COLORS["text"],
    "fontFamily": FONTS["mono"],
    "fontSize": "17px",
    "fontWeight": "normal",
    "textAlign": "left",
    "margin": "0 0 12px 0",
}

CARD_BODY_STYLE = {
    "color": COLORS["text"],
    "fontFamily": FONTS["ui"],
    "margin": "0 0 12px 0",
}

FORMULA_BOX_STYLE = {
    "fontFamily": FONTS["mono"],
    "fontSize": "13px",
    "color": COLORS["text"],
    "background": "rgba(255, 255, 255, 0.04)",
    "borderLeft": f"3px solid {COLORS['accent']}",
    "borderRadius": "4px",
    "padding": "8px 12px",
    "margin": "0 0 10px 0",
}

# --------------------------------------------------
# Grids/layout

# Row of KPIs
KPI_GRID_STYLE = {
    "display": "grid",
    "gridTemplateColumns": "repeat(auto-fit, minmax(min(100%, 220px), 1fr))",
    "gap": "14px",
    "width": "100%",
    "flex": "0 0 auto",
}

# Grid of chart cards
CHART_GRID_STYLE = {
    "display": "grid",
    "gridTemplateColumns": "repeat(auto-fit, minmax(min(100%, 380px), 1fr))",
    "gridAutoRows": "minmax(360px, 1fr)",
    "gap": "14px",
    "width": "100%",
    "flex": "1",
    "minWidth": "0",
    "minHeight": "0",
}

# --------------------------------------------------
# Overview tab
OVERVIEW_KPI_GRID_STYLE = {
    **KPI_GRID_STYLE,
    "gridTemplateColumns": "repeat(auto-fit, minmax(min(100%, 190px), 1fr))",
}

OVERVIEW_KPI_VALUE_STYLE = {
    "color": COLORS["accent_light"],
    "fontSize": "24px",
}

OVERVIEW_VISUAL_GRID_STYLE = {
    "display": "grid",
    "gridTemplateColumns": "minmax(0, 3fr) minmax(0, 2fr)",
    "gap": "14px",
    "width": "100%",
    "minWidth": "0",
}

OVERVIEW_VISUAL_CARD_STYLE = {
    **CHART_CARD_STYLE,
    "height": "390px",
    "boxSizing": "border-box",
}

OVERVIEW_QUESTION_GRID_STYLE = {
    "display": "grid",
    "gridTemplateColumns": "repeat(auto-fit, minmax(min(100%, 220px), 1fr))",
    "gap": "14px",
    "width": "100%",
}


OVERVIEW_QUESTION_CARD_STYLE = {
    **CHART_CARD_STYLE,
    "minHeight": "190px",
}

OVERVIEW_ANSWER_STYLE = {
    **CARD_BODY_STYLE,
    "flex": "1",
    "lineHeight": "1.5",
}

OVERVIEW_LINK_STYLE = {
    "alignSelf": "flex-start",
    "border": "0",
    "borderLeft": f"3px solid {COLORS['accent']}",
    "borderRadius": "4px",
    "padding": "7px 10px",
    "backgroundColor": COLORS["surface_hover"],
    "color": COLORS["accent_light"],
    "fontFamily": FONTS["mono"],
    "fontSize": "12px",
    "cursor": "pointer",
}

OVERVIEW_DETAILS_STYLE = {
    **CARD_STYLE,
    "padding": "12px 16px",
    "color": COLORS["text"],
}

OVERVIEW_DETAILS_SUMMARY_STYLE = {
    "color": COLORS["text_strong"],
    "fontFamily": FONTS["mono"],
    "cursor": "pointer",
    "marginBottom": "10px",
}

# --------------------------------------------------
# Data tab
DATA_CHART_STYLE = {
    **CHART_CARD_STYLE,
    "flex": "1",
    "minHeight": "380px",
}

DATA_FILTER_ROW_STYLE = {
    "display": "flex",
    "alignItems": "center",
    "justifyContent": "space-between",
    "flexWrap": "wrap",
    "gap": "12px",
    "marginBottom": "10px",
}

DATA_TABLE_DETAILS_STYLE = {
    **CARD_STYLE,
    "padding": "14px",
    "color": COLORS["text"],
}

DATA_TABLE_SUMMARY_STYLE = {
    "color": COLORS["text_strong"],
    "cursor": "pointer",
    "fontFamily": FONTS["mono"],
    "fontSize": "17px",
}

DATA_RESOURCE_CARD_STYLE = {
    **CARD_STYLE,
    "display": "flex",
    "alignItems": "center",
    "justifyContent": "space-between",
    "flexWrap": "wrap",
    "gap": "12px",
    "padding": "14px 18px",
    "color": COLORS["text"],
}

DATA_TABLE_HEADER_STYLE = {
    "margin": "0",
    "flex": "1",
    "fontFamily": FONTS["mono"],
    "marginBottom": "10px",
}

DATA_LINK_STYLE = {
    "color": COLORS["accent_light"],
    "fontFamily": FONTS["mono"],
    "textDecoration": "none",
}

# --------------------------------------------------
# Pipeline tab

# Outer grid 3L 1R
PIPELINE_LAYOUT_STYLE = {
    "display": "grid",
    "gridTemplateColumns": "minmax(0, 1fr) minmax(0, 1fr)",
    "gridTemplateRows": "minmax(0, 1fr)",
    "gap": "14px",
    "width": "100%",
    "flex": "1",
    "minWidth": "0",
    "minHeight": "560px",
}

PIPELINE_COLUMN_STYLE = {
    "display": "flex",
    "flexDirection": "column",
    "gap": "14px",
    "minWidth": 0,
    "minHeight": 0,
}

PIPELINE_CARD_STYLE = {
    **CHART_CARD_STYLE,
    "display": "flex",
    "flexDirection": "column",
    "minHeight": 0,
    "boxSizing": "border-box",
}

PIPELINE_KPI_STYLE = {
    **KPI_CARD_STYLE,
    "flex": "0 0 auto",
    "height": "auto",
    "minHeight": 0,
    "padding": "10px 14px",
}

# Images
PIPELINE_IMAGE_STYLE = {
    **FILL,
    "display": "block",
    "objectFit": "contain",
}

PIPELINE_DIAGRAM_IMAGE_STYLE = {
    **PIPELINE_IMAGE_STYLE,
    "maxHeight": "200px",
}

ERD_IMAGE_STYLE = {
    **PIPELINE_IMAGE_STYLE,
    "flex": "1",
    "minHeight": 0,
    "width": "100%",
}

# --------------------------------------------------
# BA tab

BA_COLOR_BAR = {
    "orientation": "h",
    "x": 0.5,
    "xanchor": "center",
    "y": -0.02,
    "yanchor": "top",
    "len": 0.5,
    "thickness": 12,
    "tickfont": {"color": COLORS["text"], "family": FONTS["mono"]},
    "outlinewidth": 0,
}

# --------------------------------------------------
# Weather tab

WEATHER_LAYOUT_STYLE = {
    "display": "grid",
    "gridTemplateColumns": "repeat(4, minmax(0, 1fr))",
    "gridTemplateRows": "minmax(320px, 1.15fr) minmax(280px, 0.85fr)",
    "gridTemplateAreas": '"controls demand demand demand" "code code wind solar"',
    "gap": "14px",
    "width": "100%",
    "flex": "1",
    "minWidth": "0",
    "minHeight": "0",
}

WEATHER_CONTROLS_STYLE = {
    **CARD_STYLE,
    "gridArea": "controls",
    "display": "flex",
    "flexDirection": "column",
    "gap": "14px",
    "minWidth": "0",
    "padding": "14px",
}

WEATHER_KPI_GRID_STYLE = {
    **KPI_GRID_STYLE,
    "gridTemplateColumns": "1fr",
    "gap": "14px",
}

# --------------------------------------------------
# Plotly
GRAPH_STYLE = {
    **FILL,
    "flex": "1",
}

PLOTLY_FONT = {"color": COLORS["text"], "family": FONTS["mono"]}

PLOTLY_AXIS_STYLE = {
    "gridcolor": COLORS["border"],
    "zerolinecolor": COLORS["border_strong"],
    "tickfont": {**PLOTLY_FONT, "color": COLORS["text_muted"]},
    "title_font": PLOTLY_FONT,
}

PLOTLY_LAYOUT_STYLE = {
    "template": "plotly_dark",
    "paper_bgcolor": COLORS["surface"],
    "plot_bgcolor": COLORS["surface"],
    "font": PLOTLY_FONT,
    "title": {"x": 0.03, "xanchor": "left", "font": {"size": 17}},
    "margin": {"l": 70, "r": 24, "t": 60, "b": 65},
    "autosize": True,
    "legend": {"font": PLOTLY_FONT},
}
