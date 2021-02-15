import os, json
import dash
import dash_html_components as html
import dash_bootstrap_components as dbc
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import plotly.express as px
import pandas as pd

from dash.dependencies import Output, Input

import mapping
import contrib
import plotting

from mec_query import Candidate, Contribution, Contributor

server = Flask(__name__)
server.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
server.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(server)

app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)
candidates = Candidate.query.all()

mec_ids = ["C201499", "C201099", "C201500", "C211544"]
mec_df = pd.read_sql(db.session.query(Contribution).statement, db.session.bind)

root_layout = html.Div(
    id="root",
    children=[
        mapping.get_side_panel_layout(candidates, mec_df),
        mapping.get_map_panel_zip_layout(),
        html.Div(id="floatbox-holder")
    ],
    style={"display": "flex", "flexDirection": "row", "margin": 0},
)

app.layout = root_layout

@app.callback(
    Output("side-panel-form", "children"),
    [Input("fundraising-graph", "clickData"), Input("close-floatbox", "click")],
)
def click_bar_graph(clicked_data):
    if clicked_data is not None:
        clicked_name = clicked_data["points"][0]["label"]
        return plotting.candidate_funding_details(clicked_name, mec_df)
    else:
        return plotting.create_candidate_funds_bar_plot(candidates, mec_df)

@app.callback(
    Output("floatbox-holder", 'children'), 
    [Input("zips-geojson", "click_feature")])
def zip_click(feature):
    if feature is not None:
        return [html.Div([
            f"ZIP Code {feature['properties']['ZCTA5CE10']}",
            html.Br(),
            f"Total funds contributed for Mayor's race: {str(feature['properties']['total_mayor_donations'])}"
        ], id='floatbox')]
    else:
        return None

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
    
    # contribution_df = pd.read_sql(
    #     db.session.query(Contribution).statement, db.session.bind
    # )
    # contributor_df = pd.read_sql(
    #     db.session.query(Contributor).statement, db.session.bind
    # )
    # mec_df = contribution_df.merge(
    #     contributor_df, left_on="contributor_id", right_index=True
    # )
    # zip_geojson_data = contrib.build_zip_amount_geojson(mec_df, mec_id)
    # return zip_geojson_data


# @app.callback(
#     Output("zips-geojson", "data"),
#     [Input("candidate-select", "value")])
# def display_choropleth(mec_id):
#     contribution_df = pd.read_sql(db.session.query(Contribution).statement, db.session.bind)
#     contributor_df = pd.read_sql(db.session.query(Contributor).statement, db.session.bind)
#     mec_df = contribution_df.merge(contributor_df, left_on="contributor_id", right_index=True)
#     zip_geojson_data = contrib.build_zip_amount_geojson(mec_df, mec_id)
#     return zip_geojson_data

if __name__ == "__main__":
    app.run_server(debug=True)
