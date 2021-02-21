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

import locale

locale.setlocale(locale.LC_ALL, "en_US.UTF-8")

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

# @app.callback(
#     [Output("zips-geojson", "hideout")],
#     [Input("fundraising-graph", "hoverData")],
# )
# def display_choropleth(hovered_data):
#     if hovered_data is not None:
#         candidate_row = db.session.query(Candidate).filter_by(name=hovered_data["points"][0]["label"]).first()
#         mec_id = candidate_row.mec_id
#         color_prop = "mec_donazzzzzzzzzzzzzzzzzztion_"+mec_id
#     else:
#         color_prop = "total_mayor_donations"
#     hideout = bootstrap_stuff.build_choropleth_hideout(color_prop)
#     return [hideout]

# Candidate Selected: Look at stats from that candidate
# @app.callback(
#     [Output("candidate_info_collapse", "is_open"), Output("candidate_info_collapse", "children"), Output("zips-geojson", "hideout")],
#     [Input("fundraising-graph", "clickData")],
#     [State("candidate_info_collapse", "is_open")]
# )
# def toggle_collapse(clicked_data, is_open):
#     if clicked_data is not None:
#         candidate_row = db.session.query(Candidate).filter_by(name=clicked_data["points"][0]["label"]).first()
#         mec_id = candidate_row.mec_id
#         color_prop = "mec_donation_"+mec_id
#         hideout = bootstrap_stuff.build_choropleth_hideout(color_prop)
#         return (True, [bootstrap_stuff.get_candidate_info_card(candidate_row)], hideout)
#     hideout = bootstrap_stuff.build_choropleth_hideout("total_mayor_donations")
#     return (False, [], hideout)


@app.callback(
    Output("testingDiv", "children"), [Input("geojson-layer-control", "baseLayer")]
)
def layer_change(base_layer):
    return "You are viewing contributions from each " + base_layer


@app.callback(
    [
        Output("geojson-layer-control", "baseLayer"),
        Output("precinct-button", "active"),
        Output("neighborhood-button", "active"),
        Output("zip-button", "active"),
    ],
    [
        Input("precinct-button", "n_clicks"),
        Input("neighborhood-button", "n_clicks"),
        Input("zip-button", "n_clicks"),
    ],
)
def layer_button_click(precinct_clicks, neighborhood_clicks, zip_clicks):
    changed_id = [p["prop_id"] for p in dash.callback_context.triggered][0]
    if "precinct-button" in changed_id:
        return ["precinct", True, False, False]
    elif "neighborhood-button" in changed_id:
        return ["neighborhood", False, True, False]
    elif "zip-button" in changed_id:
        return ["zip", False, False, True]
    else:
        return ["neighborhood", False, True, False]


@app.callback(
    [
        Output("floatbox-neighborhood", "children"),
        Output("floatbox-neighborhood", "className"),
    ],
    [
        Input("neighborhood-geojson", "click_feature"),
        Input("card-box-close-neighborhood", "n_clicks"),
    ],
)
def neighborhood_click(feature, n_clicks):
    class_name = "displayNone"
    header_text = "Error"
    card_contents = bootstrap_stuff.get_floatbox_card_contents("neighborhood")

    if feature:
        header_text = feature["properties"]["NHD_NAME"]
        body_contents = [
            html.Strong("Total monetary donations: "),
            html.Span(
                locale.currency(
                    feature["properties"]["total_monetary_donations"], grouping=True
                )
            ),
        ]
        class_name = "floatbox"
        card_contents = bootstrap_stuff.get_floatbox_card_contents(
            "neighborhood", header_text, body_contents
        )

    if n_clicks:
        class_name = "displayNone"

    return [card_contents, class_name]


@app.callback(
    [Output("floatbox-precinct", "children"), Output("floatbox-precinct", "className")],
    [
        Input("precincts-geojson", "click_feature"),
        Input("card-box-close-precinct", "n_clicks"),
    ],
)
def precinct_click(feature, n_clicks):
    class_name = "displayNone"
    header_text = "Error"
    card_contents = bootstrap_stuff.get_floatbox_card_contents("precinct")

    if feature:
        header_text = f"Ward {feature['properties']['WARD10']}, Precinct {feature['properties']['PREC10']}"
        body_contents = [
            html.Strong("Total monetary donations: "),
            html.Span(
                locale.currency(
                    feature["properties"]["total_monetary_donations"], grouping=True
                )
            ),
        ]
        class_name = "floatbox"
        card_contents = bootstrap_stuff.get_floatbox_card_contents(
            "precinct", header_text, body_contents
        )

    if n_clicks:
        class_name = "displayNone"

    return [card_contents, class_name]


if __name__ == "__main__":
    app.run_server(debug=True)
