from dash.testing.application_runners import import_app


# def test_app(dash_duo):
#     pass


#     app = import_app("dashboard")
#     dash_duo.start_server(app)


def test_layout(app):
    with app.app_context():
        from dsadata.bootstrap_stuff import get_sidebar_layout

        layout = get_sidebar_layout()
        assert layout.className == "remove-padding"
        main_div = layout.children
        assert len(main_div) == 2
        row = main_div[0]
        assert len(row.children) == 3


# def test_ward_click(dash_duo):
#     app = import_app("app")
#     dash_duo.start_server(app)