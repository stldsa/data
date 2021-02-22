from mec_query import Candidate, Contribution
from plotting import create_candidate_funds_bar_plot
import pandas as pd


# def test_create_candidate_funds_bar_plot(db_session):
#     candidates = Candidate.query.all()
#     mec_df = pd.read_sql(db_session.query(Contribution).statement, db_session.bind)


def test_candidate_funds_bar_plot():
    data = [
        ["Cara Spencer", 182000, 1045, 144.82],
        ["Tishaura Jones", 156000, 593, 305.38],
    ]
    df = pd.DataFrame(
        data, columns=["Candidate", "$ Raised", "# of Donations", "Avg Donation"]
    )

    fig = create_candidate_funds_bar_plot(df)

    assert fig.data


def test_contribution_stats_for_candidate(tishaura):
    contributions_df = Contribution.df
    assert tishaura.stats["$ Raised"] == sum(
        contributions_df[contributions_df["Candidate"]]
    )


def test_contributions_df():
    assert len(Contribution.df.columns)