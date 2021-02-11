import os
import json
import pandas as pd
import plotly.express as px 
import dash_bootstrap_components as dbc
import dash_leaflet as dl 
import dash_leaflet.express as dlx
import dash_core_components as dcc 
import dash_html_components as html


pd.options.plotting.backend = "plotly"

def create_contribution_df(mec_ids):
    li = []
    for filename in os.listdir('data/mec'):
        df = pd.read_csv('data/mec/' + filename, index_col=None, header=0, parse_dates=['Date'])
        df.loc[:, 'ZIP5'] = df.loc[:, 'Zip'].astype(str).str[:5]
        df = df[df[' MECID'].isin(mec_ids)]
        li.append(df)
    frame = pd.concat(li, axis=0, ignore_index=True)
    return frame

def sum_funds_by_zip_and_mecid(mec_df):
    mec_df.loc[:, 'zip5'] = mec_df.loc[:, 'Zip'].astype(str).str[:5]
    donation_sum_by_zip = mec_df.groupby(by=['mec_id', 'zip5'], as_index=False).agg({'Amount':'sum'})
    return donation_sum_by_zip

def sum_funds_by_mecid(mec_df):
    donations_sum = mec_df.groupby(by=['mec_id']).agg({'amount':'sum'})
    return donations_sum

def sum_funds_by_zip(mec_df, mec_id=None):
    if mec_id is None:
        zip_df = mec_df.groupby(by=['zip5']).agg({'amount':'sum'})
    else:
        cand_df = mec_df[mec_df['mec_id'] == mec_id]
        zip_df = cand_df.groupby(by=['zip5']).agg({'amount':'sum'})
    return zip_df

def build_zip_amount_geojson(df, mec_id=None):
    if mec_id is None:
        zip_df = df.groupby(by=['zip5']).agg({'amount':'sum'})
    else:
        cand_df = df[df['mec_id'] == mec_id]
        zip_df = cand_df.groupby(by=['zip5']).agg({'amount':'sum'})
    zip_geojson_path = "data/geojson/stl-region-zip_rw.geojson"
    with open(zip_geojson_path) as read_file:
        zip_geojson_data = json.load(read_file)

    for feat in zip_geojson_data['features']:
        if feat['properties']['ZCTA5CE10'] in zip_df.index:
            feat['properties']['Amount'] = zip_df.loc[feat['properties']['ZCTA5CE10']].amount
        else:
            feat['properties']['Amount'] = 0
    return zip_geojson_data
