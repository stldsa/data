import os
import pytest
from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from dsadata.mec_query import Candidate, Contribution

load_dotenv()


@pytest.fixture(scope="session")
def db_url():
    return os.getenv("DATABASE_URL")


# @pytest.fixture(scope='session')
# def database(db_url):


#     @request.addfinalizer
#     def drop_database():
#         drop_postgresql_database(pg_user, pg_host, pg_port, pg_db, 9.6)


@pytest.fixture(scope="session")
def app():
    app = Flask(__name__)
    database = SQLAlchemy()
    database.init_app(app)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    with app.app_context():
        from dsadata.dashboard import init_dashboard

        app = init_dashboard(app)

        return app
    return app


@pytest.fixture(scope="session")
def _db(app):

    db = SQLAlchemy(app=app)

    return db


@pytest.fixture(scope="session")
def tishaura():
    return Candidate(name="Tishaura Jones")


@pytest.fixture(scope="session")
def contributions_df():
    return Contribution.df


@pytest.fixture(scope="session")
def candidates_df(app):
    with app.app_context():
        return Candidate.df()


@pytest.fixture(scope="session")
def contributions_candidates_df(contributions_df, candidates_df):
    return contributions_df.merge(candidates_df, on=["mec_id"])