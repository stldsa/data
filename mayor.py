import os
import dash
import dash_html_components as html
import dash_bootstrap_components as dbc
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

server = Flask(__name__)
server.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
server.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(server)


class Candidate(db.Model):
    name = db.Column(db.String, primary_key=True)


db.create_all()
db.session.commit()

app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)
candidates = Candidate.query.all()
candidate_columns = [
    dbc.Col(html.P(candidate.name), className="candidate") for candidate in candidates
]
app.layout = dbc.Row(id="candidates-row", children=candidate_columns)

if __name__ == "__main__":
    app.run_server(debug=True)