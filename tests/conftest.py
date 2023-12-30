import os
import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from donation_map import init_app
from donation_map.mec_query import Candidate, Contribution


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
    app = init_app()
    return app


@pytest.fixture(scope="session")
def _db(app):

    db = SQLAlchemy(app=app)

    return db


@pytest.fixture(scope="session")
def tishaura(app):
    with app.app_context():
        return Candidate(name="Tishaura Jones")


@pytest.fixture(scope="session")
def contributions_df(app):
    with app.app_context():
        return Contribution.df


@pytest.fixture(scope="session")
def candidates_df(app):
    with app.app_context():
        return Candidate.df()


@pytest.fixture(scope="session")
def contributions_candidates_df(contributions_df, candidates_df):
    return contributions_df.merge(candidates_df, on=["mec_id"])