import results_handler as rh

import datatest as dt
import pytest


@pytest.fixture
def sample_results_csv_path():
    return 'data/tidy-results/tidy-results-full.csv'

sample_results_columns = [
    "election_date",
    "ward",
    "precinct",
    "contest_name",
    "candidate_selection",
    "vote_type",
    "vote_count"
]

@pytest.fixture
def results_indexes():
    return ["election_date"]

@pytest.fixture
def sample_results_df(sample_results_csv_path):
    return rh.read_results_csv(sample_results_csv_path)

@pytest.fixture
def sample_election_date():
    return '6/23/2020'
sample_election_num_rows = 360

@pytest.fixture
def sample_contest_name():
    return 'WD 4 ALDERMAN'
sample_contest_num_rows = 144

@pytest.fixture
def sample_candidate_name():
    return 'DWINDERLIN EVANS'
sample_candidate_num_rows = 72

@pytest.fixture
def sample_ward():
    return 4
sample_ward_vote_count_by_precinct = [73, 84, 26, 39, 36, 26, 49,  6, 10,  5]

def test_read_results_csv(sample_results_csv_path, results_indexes):
    results_data = rh.read_results_csv(sample_results_csv_path)   
    dt.validate(results_data.columns, sample_results_columns)
    
def test_narrow_to_election(sample_results_df, sample_election_date):
    elec_df = rh.narrow_to_election(sample_results_df, sample_election_date)
    num_rows = len(elec_df.index)
    dt.validate(num_rows, sample_election_num_rows)
    
def test_narrow_to_contest(sample_results_df, sample_election_date, sample_contest_name):
    elec_df = rh.narrow_to_election(sample_results_df, sample_election_date)
    contest_df = rh.narrow_to_contest(elec_df, sample_contest_name)
    num_rows = len(contest_df.index)
    print(num_rows)
    dt.validate(num_rows, sample_contest_num_rows)

def test_narrow_to_candidate(sample_results_df, sample_election_date, sample_contest_name, sample_candidate_name):
    elec_df = rh.narrow_to_election(sample_results_df, sample_election_date)
    contest_df = rh.narrow_to_contest(elec_df, sample_contest_name)
    candidate_df = rh.narrow_to_candidate(contest_df, sample_candidate_name)
    num_rows = len(candidate_df.index)
    dt.validate(num_rows, sample_candidate_num_rows)
    
def test_sum_votes_by_precinct(sample_results_df, sample_election_date, sample_contest_name, sample_candidate_name, sample_ward):
    elec_df = rh.narrow_to_election(sample_results_df, sample_election_date)
    contest_df = rh.narrow_to_contest(elec_df, sample_contest_name)
    candidate_df = rh.narrow_to_candidate(contest_df, sample_candidate_name)
    summed_df = rh.sum_votes_by_precinct(candidate_df)
    ward_df = summed_df[summed_df["ward"] == sample_ward]
    dt.validate(ward_df.vote_count.values, sample_ward_vote_count_by_precinct)
    
    
    
    