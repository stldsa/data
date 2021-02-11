import os, json
import dash
import dash_html_components as html
import dash_bootstrap_components as dbc
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import plotly.express as px
import pandas as pd

import mapping
import contrib
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
        html.Div(id="float-box"),
    ],
    style={"display": "flex", "flexDirection": "row", "margin": 0},
)

app.layout = root_layout


@app.callback(
    [dash.dependencies.Output("panel-side", "className")],
    [dash.dependencies.Input("expand-side-swith", "value")],
)
def toggle_expand(value):
    if not value:
        return ["SidePanel_NotExpanded"]
    else:
        return ["SidePanel_Expanded"]


@app.callback(
    dash.dependencies.Output("float-box", "children"),
    [dash.dependencies.Input("zips-geojson", "hover_feature")],
)
def zip_hover(feature):
    if feature is not None:
        return False


@app.callback(
    dash.dependencies.Output("candidate-select", "value"),
    [dash.dependencies.Input("fundraising-graph", "clickData")],
)
def bar_click(clicked_data):
    if clicked_data is not None:
        # db.session.commit()
        clicked_name = clicked_data["points"][0]["label"]
        candidate_row = db.session.query(Candidate).filter_by(name=clicked_name).first()
        return candidate_row.mec_id


@app.callback(
    dash.dependencies.Output("zips-geojson", "data"),
    [dash.dependencies.Input("candidate-select", "value")],
)
def display_choropleth(mec_id):
    contribution_df = pd.read_sql(
        db.session.query(Contribution).statement, db.session.bind
    )
    contributor_df = pd.read_sql(
        db.session.query(Contributor).statement, db.session.bind
    )
    mec_df = contribution_df.merge(
        contributor_df, left_on="contributor_id", right_index=True
    )
    zip_geojson_data = contrib.build_zip_amount_geojson(mec_df, mec_id)
    return zip_geojson_data


if __name__ == "__main__":
    app.run_server(debug=True)