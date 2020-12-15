import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

import pandas as pd
import json

df = pd.read_csv("data/tabular_data/2020-general-election.csv", dtype={"Ward": str})
with open("data/geodata/WARDS_2010.json") as read_file:
    wards_geojson = json.load(read_file)

# TODO: Figure out a better way to handle this candidates stuff, dynamically and by election, ideally
candidates = [
    "Trump",
    "Biden",
    "Prop D Yes",
    "Prop D No",
    "Prop R Yes",
    "Prop R No",
    "Prop 1 Yes",
    "Prop 1 No",
]

app = dash.Dash(__name__)

app.layout = html.Div(
    [
        html.P("Candidate:"),
        dcc.RadioItems(
            id="candidate",
            options=[{"value": x, "label": x} for x in candidates],
            value=candidates[0],
            labelStyle={"display": "inline-block"},
        ),
        dcc.Graph(id="choropleth", style={"height": "80vh"}),
    ]
)


@app.callback(Output("choropleth", "figure"), [Input("candidate", "value")])
def display_choropleth(candidate):
    fig = px.choropleth(
        df,
        geojson=wards_geojson,
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