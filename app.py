import os, json
import dash
import dash_html_components as html
import dash_bootstrap_components as dbc
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

import pandas as pd
from dash.dependencies import Output, Input

import mapping
import contrib
import plotting

from mec_query import Candidate, Contribution, Contributor
from bootstrap_stuff import get_sidebar_layout, show_zip_click_card

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
        hovered_name = hovered_data["points"][0]["label"]
        candidate_row = db.session.query(Candidate).filter_by(name=hovered_name).first()
        mec_id = candidate_row.mec_id
        color_prop = "mec_donation_"+mec_id
    else:
        color_prop = "total_mayor_donations"
    hideout = dict(colorscale=mapping.fundraising_colorscale, classes=mapping.fundraising_classes, style=mapping.fundraising_style, colorProp=color_prop)
    return [hideout]

@app.callback(
    Output("floatbox-holder", "children"),
    [Input("zips-geojson", "click_feature")]
)
def zip_click(feature):
    if feature is not None:
        return show_zip_click_card(feature)
    else:
        return None

if __name__ == "__main__":
    app.run_server(debug=True)
