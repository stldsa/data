import os
import dash
import dash_html_components as html
import dash_bootstrap_components as dbc
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

import mapping
import contrib

load_dotenv()

server = Flask(__name__)
server.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
server.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(server)


class Candidate(db.Model):
    name = db.Column(db.String, primary_key=True)
    mec_id = db.Column(db.String(10), unique=True, nullable=False)


db.create_all()
db.session.commit()

app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)
candidates = Candidate.query.all()

mec_ids = ['C201499', 'C201099', 'C201500', 'C211544']
df = contrib.create_contribution_df(mec_ids)

root_layout = html.Div(
    id='root',
    children=[
        mapping.get_side_panel_layout(candidates, df),
        mapping.get_map_panel_layout(df)
    ],
    style={"display": "flex", "flexDirection": "row", "margin": 0}
)

app.layout = root_layout


@app.callback(
    [dash.dependencies.Output('panel-side', 'className')],
    [dash.dependencies.Input('expand-side-swith', 'value')])
def toggle_expand(value):
    if not value:
        return ["SidePanel_NotExpanded"]
    else:
        return ["SidePanel_Expanded"]

if __name__ == "__main__":
    app.run_server(debug=True)