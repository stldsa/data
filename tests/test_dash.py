from dash.testing.application_runners import import_app


# def test_app(dash_duo):
#     pass


#     app = import_app("dashboard")
#     dash_duo.start_server(app)


def test_layout():
    from dsadata.bootstrap_stuff import get_sidebar_layout

    layout = get_sidebar_layout()
    assert layout.className == "remove-padding"
    main_div = layout.children
    assert len(main_div) == 1
    row = main_div[0]
    assert len(row.children) == 2

    info_bar = row.children[0]
    map = row.children[1]

    print(dir(info_bar))
    print(dir(map))


def test_ward_click(dash_duo):
    app = import_app("app")
    dash_duo.start_server(app)