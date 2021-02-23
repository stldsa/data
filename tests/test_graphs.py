# from dsadata.mec_query import Candidate, Contribution
# from dsadata.plotting import create_candidate_funds_bar_plot
import pandas as pd


# # def test_create_candidate_funds_bar_plot(db_session):
# #     candidates = Candidate.query.all()
# #     mec_df = pd.read_sql(
#           db_session.query(Contribution).statement,db_session.bind
#       )


# def test_candidate_funds_bar_plot():
#     data = [
#         ["Cara Spencer", 182000, 1045, 144.82],
#         ["Tishaura Jones", 156000, 593, 305.38],
#     ]
#     df = pd.DataFrame(
#         data, columns=[
#           "Candidate",
#           "$ Raised",
#           "# of Donations",
#           "Avg Donation"
#       ]
#     )

#     fig = create_candidate_funds_bar_plot(df)

#     assert fig.data


# def test_contribution_stats_for_candidate(
#   tishaura, contributions_candidates_df
# ):
#     df = contributions_candidates_df
#     assert "name" in df.columns.to_list()
#     tishaura_contributions = df[df["name"] == "Tishaura Jones"]
#     assert tishaura.total_raised == sum(tishaura_contributions["amount"])


# # def test_candidate_contributions(tishaura):
# #     assert tishaura.contributions


def test_candidates_df_returns_dataframe(candidates_df, app):
    with app.app_context():
        assert isinstance(candidates_df, pd.DataFrame)


# # def test_tishaura_info_accurate(tishaura):
# #     assert tishaura.mec_id == 1