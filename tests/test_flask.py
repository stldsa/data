from dsadata import init_app
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


def test_root_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.content_type == "text/html; charset=utf-8"


def test_init_app():
    app = Flask(__name__)
    database = SQLAlchemy()
    database.init_app(app)
    assert app.config["SQLALCHEMY_DATABASE_URI"]


def test_app_fixture(app):
    assert app.config["SQLALCHEMY_DATABASE_URI"]