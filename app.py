import os, json
import dash
import dash_html_components as html
import dash_bootstrap_components as dbc
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

import pandas as pd
from dash.dependencies import Output, Input, State

import mapping
import contrib
import plotting
import bootstrap_stuff

from mec_query import Candidate, Contribution, Contributor
from bootstrap_stuff import get_sidebar_layout, get_zip_click_card

load_dotenv()

server = Flask(__name__)
server.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
server.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(server)

app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)
app.layout = get_sidebar_layout(db)

@app.callback(
    [Output("zips-geojson", "hideout")],
    [Input("fundraising-graph", "hoverData")],
)
def display_choropleth(hovered_data):
    if hovered_data is not None:
        candidate_row = db.session.query(Candidate).filter_by(name=hovered_data["points"][0]["label"]).first()
        mec_id = candidate_row.mec_id
        color_prop = "mec_donation_"+mec_id
    else:
        color_prop = "total_mayor_donations"
    hideout = bootstrap_stuff.build_choropleth_hideout(color_prop)
    return [hideout]

# Candidate Selected: Look at stats from that candidate
@app.callback(
    [Output("candidate_info_collapse", "is_open"), Output("candidate_info_collapse", "children")],
    [Input("fundraising-graph", "clickData")],
    [State("candidate_info_collapse", "is_open")]
)
def toggle_collapse(clicked_data, is_open):
    if clicked_data is not None:
        candidate_row = db.session.query(Candidate).filter_by(name=clicked_data["points"][0]["label"]).first()
        return (True, [bootstrap_stuff.get_candidate_info_card(candidate_row)])
    return (False, [])

@app.callback(
    [Output("floatbox-holder", "children"), Output("floatbox-holder", "className")],
    [Input("zips-geojson", "click_feature"), Input("zip-box-close", "n_clicks")]
)
def zip_click(feature, n_clicks):
    if feature and not n_clicks: 
        class_name = "displayBlock"
    else:
        class_name = "displayNone"

    return [ bootstrap_stuff.get_zip_click_card(feature), class_name ]

if __name__ == "__main__":
    app.run_server(debug=True)
