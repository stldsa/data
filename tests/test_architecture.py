import pandas as pd
from dsadata.mec_query import Candidate


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