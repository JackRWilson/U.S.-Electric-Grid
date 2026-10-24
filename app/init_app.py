from dash import Dash
from styles import COLORS

app = Dash(__name__)
app.index_string = app.index_string.replace(
    "</head>",
    (
        "<style>"
        "html,body,#react-entry-point,#_dash-app-content{"
        "width:100%;height:100%;min-height:100%;margin:0;"
        f"background:{COLORS['page']};"
        "}"
        "body{overflow:hidden;}"
        "</style></head>"
    ),
)
