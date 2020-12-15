import json
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

df = pd.read_csv("data/tabular_data/2020-general-election.csv")
with open("data/geodata/WARDS_2010.json") as f:
    wards = json.load(f)

options = df.columns.names[1:]
app = dash.Dash(__name__)
print(options)

app.layout = html.Div(
    [
        html.P("Candidate:"),
        dcc.RadioItems(
            id="candidate",
            options=[{"value": x, "label": x} for x in options],
            labelStyle={"display": "inline-block"},
        ),
        dcc.Graph(id="choropleth", style={"height": "80vh"}),
    ]
)


@app.callback(Output("choropleth", "figure"), [Input("candidate", "value")])
def display_choropleth(candidate):
    fig = px.choropleth(
        df,
        geojson=wards,
        color=candidate,
        locations="Ward",
        featureidkey="properties.Ward",
        projection="mercator",
        range_color=[0, 6500],
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig


app.run_server(debug=True)