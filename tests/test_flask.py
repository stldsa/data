from donation_map import init_app


def test_root_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.content_type == "text/html; charset=utf-8"


def test_init_app():
    app = init_app()
    assert app.config["SQLALCHEMY_DATABASE_URI"]


def test_app_fixture(app):
    assert app.config["SQLALCHEMY_DATABASE_URI"]