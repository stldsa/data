import pandas as pd
from database import db


def test_read_sql_table(db_engine, db_session):
    df = pd.read_sql_table("candidates", db_engine)
    pass


def test_candidate_class():
    candidate = Candidate(name="Lyda Krewson")
    assert candidate.name == "Lyda Krewson"
    # assert str(candidate.id) == "None"


def test_add_candidate(db_session):
    lyda = Candidate(name="Lyda Krewson")
    db_session.add(lyda)
    # lyda2 = db_session.query(Candidate).filter_by(name="Lyda Krewson").first()
    # candidate = db_session.query(Candidate).get(1)
    # row.set_name
    # print(table)
    # assert False