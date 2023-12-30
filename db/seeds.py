import os
from donation_map.mec_query import Candidate
import pandas as pd
import os
from sqlalchemy import create_engine
from glob import glob
from donation_map import db

candidates = pd.read_csv("dsadata/static/candidates_2021-03-02.csv")
candidates = candidates[
    ["MECID", "Candidate Name", "Committee Name", "Office Sought", "Status"]
]
candidates["Candidate Name"] = candidates["Candidate Name"].str.title()

candidates.to_sql("candidate", db.engine, if_exists="replace", index=False)
csv_files = glob("data/mec/*")
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
        "Employer",
        "Occupation",
        "Amount",
        "Contribution Type",
    ]
]
# .rename(
#     columns={
#         "CD1_A ID": "id",
#         "Date": "date",
#         " MECID": "mec_id",
#         "Latitude": "lat",
#         "Longitude": "lon",
#         "Employer": "employer",
#         "Occupation": "occupation",
#         "Amount": "amount",
#         "Contribution Type": "contribution_type",
#         "Report": "report",
#     }
# )
all_contributions.to_sql(
    "contribution", db.engine, if_exists="replace", index=False, chunksize=1000
)

# contributions = mec_query.create_contributions(mec_df)
# mec_query.insert_contributions(contributions)