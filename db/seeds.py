import os
from dsadata.mec_query import Candidate
import pandas as pd
import os
from sqlalchemy import create_engine
from glob import glob

db_uri = os.getenv("DATABASE_URL")
engine = create_engine(db_uri, echo=True)
# Right now only doing mayoral race, but update as necessary
candidates = pd.read_csv("data/candidates_2021-03-02.csv")
candidates = candidates[
    [
        "MECID",
        "Candidate Name",
        "Committee Name",
        # "Office Sought", "Status"
    ]
].rename(
    columns={
        "MECID": "mec_id",
        "Candidate Name": "name",
        "Committee Name": "committee_name",
        "Office Sought": "office_sought",
        # "Status": "status"
    }
)

candidates.to_sql("candidate", engine, if_exists="append", index=False)
csv_files = glob("data/mec_geocoded/*")
# print(csv_files)
globals().update(
    locals()
)  # so we can use pandas inside the listcomp below - https://github.com/inducer/pudb/issues/103
dataframes = [pd.read_csv(file) for file in csv_files]
all_contributions = pd.concat(dataframes)
all_contributions = all_contributions[
    [
        "CD1_A ID",
        "Date",
        " MECID",
        "Latitude",
        "Longitude",
        "Employer",
        "Occupation",
        "Amount",
        "Contribution Type",
    ]
].rename(
    columns={
        "CD1_A ID": "id",
        "Date": "date",
        " MECID": "mec_id",
        "Latitude": "lat",
        "Longitude": "lon",
        "Employer": "employer",
        "Occupation": "occupation",
        "Amount": "amount",
        "Contribution Type": "contribution_type",
        "Report": "report",
    }
)
all_contributions.to_sql(
    "contribution", engine, if_exists="append", index=False, chunksize=1000
)

# contributions = mec_query.create_contributions(mec_df)
# mec_query.insert_contributions(contributions)