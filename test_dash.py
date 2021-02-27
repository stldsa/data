from dash.testing.application_runners import import_app


def test_ward_click(dash_duo):
    app = import_app("app")
    dash_duo.start_server(app)