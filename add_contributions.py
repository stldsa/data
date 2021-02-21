import os
import json
import pandas as pd
import geopandas as gpd

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

from app import db, Candidate, Contribution, Contributor

contribution_df = pd.read_sql(db.session.query(Contribution).statement, db.session.bind)
contributor_df = pd.read_sql(db.session.query(Contributor).statement, db.session.bind)
mec_df = contribution_df.merge(contributor_df, left_index=True, right_index=True)

# Make a geodataframe of the geocoded donations:
geocoded_mec_df = pd.read_sql(db.session.query(Contribution).filter(Contribution.lat != "Nan").statement, db.session.bind)
mec_gdf = gpd.GeoDataFrame(geocoded_mec_df, geometry=gpd.points_from_xy(geocoded_mec_df.lon, geocoded_mec_df.lat))
mec_gdf = mec_gdf.set_crs(epsg=4326)

zip_geojson_path = "data/geojson/stl-region-zip_rw.geojson"
zip_geobuf_path = "static/geobuf/stl-region-zip.pbf"
mec_query.build_donation_pbf_from_geojson(mec_gdf, mayor_mec_ids, zip_geojson_path, zip_geobuf_path)

precincts_geojson_path = "data/geojson/stl-city/precincts_rw.geojson"
precincts_geobuf_path = "static/geobuf/stl-city-precincts.pbf"
mec_query.build_donation_pbf_from_geojson(mec_gdf, mayor_mec_ids, precincts_geojson_path, precincts_geobuf_path)

nhoods_geojson_path = "data/geojson/stl-city/neighborhoods_rw.geojson"
nhoods_geobuf_path = "static/geobuf/stl-city-neighborhoods.pbf"
mec_query.build_donation_pbf_from_geojson(mec_gdf, mayor_mec_ids, nhoods_geojson_path, nhoods_geobuf_path)