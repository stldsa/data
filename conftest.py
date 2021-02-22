import os
import pytest
import flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from mec_query import Candidate

load_dotenv()


@pytest.fixture(scope="session")
def db_url():
    return os.getenv("DATABASE_URL")


@pytest.fixture(scope="session")
def app(db_url):
    #     """
    #     Create a Flask app context for the tests.
    #     """
    app = flask.Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    return app


@pytest.fixture(scope="session")
def _db(app):

    db = SQLAlchemy(app=app)

    return db


@pytest.fixture(scope="session")
def tishaura():
    return Candidate(name="Tishaura Jones")
