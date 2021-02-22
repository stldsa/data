import dash
import pytest
from dash.testing.application_runners import import_app


def test_app(dash_duo):
    app = import_app("app")
    dash_duo.start_server(app)
