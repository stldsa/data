import dash
import dash_html_components as html
from flask import Flask
from dash.testing.application_runners import import_app


def test_mayor_app(dash_duo):
    app = import_app("mayor")
    # app.layout = html.Div(id="nully-wrapper", children=0)

    dash_duo.start_server(app)

    candidates_row = dash_duo.find_element("#candidates-row")

    candidates = dash_duo.find_elements(".candidate")

    assert len(candidates) == 4
