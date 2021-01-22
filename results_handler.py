import pandas as pd

def read_results_csv(results_path):
    results_df = pd.read_csv(results_path)
#     results_df.set_index("election_date", inplace=True)
    return results_df

def narrow_to_election(results_df, election_date):
    elec_df = results_df[results_df['election_date'] == election_date]
    return elec_df

def narrow_to_contest(results_df, contest_name):
    contest_df = results_df[results_df['contest_name'] == contest_name]
    return contest_df

def narrow_to_candidate(results_df, candidate_selection):
    candidate_df = results_df[results_df['candidate_selection'] == candidate_selection]
    return candidate_df

sum_precinct_aggregation_function = {'vote_count': 'sum'}
def sum_votes_by_precinct(results_df):
    summed_df = results_df.groupby(['election_date', 'contest_name', 'candidate_selection', 'ward', 'precinct'], as_index=False).aggregate(sum_precinct_aggregation_function)
    return summed_df
