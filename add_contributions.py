import os
import json
import pandas as pd

import contrib
import mec_query
import geobuf

# Right now only doing mayoral race, but update as necessary
mayor_mec_ids = ['C201499', 'C201099', 'C201500', 'C211544']
mec_df = mec_query.build_mec_df(mayor_mec_ids)
mec_query.clear_tables() # Try commenting this out if this script is giving you issues
mec_query.create_tables()
contributions = mec_query.create_contributions(mec_df)
mec_query.insert_contributions(contributions)

from mayor import db, Candidate, Contribution, Contributor
contribution_df = pd.read_sql(db.session.query(Contribution).statement, db.session.bind)
contributor_df = pd.read_sql(db.session.query(Contributor).statement, db.session.bind)
mec_df = contribution_df.merge(contributor_df, left_index=True, right_index=True)

zip_df = mec_df.groupby(by=["zip5", "mec_id"]).agg({"amount": "sum"})
zip_total_df = mec_df.groupby(by=["zip5"]).agg({"amount": "sum"})

zip_geojson_path = "static/stl-region-zip_rw.geojson"
# TODO: Copy the above but do it for wards, neighborhoods, precincts and save the geobuf
with open(zip_geojson_path) as read_file:
    zip_geojson_data = json.load(read_file)

for feat in zip_geojson_data["features"]:
    if feat["properties"]["ZCTA5CE10"] in zip_df.index:
        mec_donations = zip_df.loc[feat["properties"]["ZCTA5CE10"]].to_dict()
        for mec_id in mec_donations["amount"]:
            amount = mec_donations["amount"][mec_id]
            feat["properties"]["mec_donation_"+mec_id] = amount
        feat["properties"]["total_mayor_donations"] = zip_total_df.loc[feat["properties"]["ZCTA5CE10"]].amount
    else:
        feat["properties"]["total_mayor_donations"] = 0

pbf = geobuf.encode(zip_geojson_data)
zip_geobuf_path = "static/geobuf/stl-region-zip.pbf"
with open(zip_geobuf_path, "wb") as write_file:
    write_file.write(pbf)