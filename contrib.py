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
    mec_df.loc[:, 'ZIP5'] = mec_df.loc[:, 'Zip'].astype(str).str[:5]
    donation_sum_by_zip = mec_df.groupby(by=[' MECID', 'ZIP5'], as_index=False).agg({'Amount':'sum'})
    return donation_sum_by_zip

def sum_funds_by_mecid(mec_df):
    donations_sum = mec_df.groupby(by=[' MECID']).agg({'Amount':'sum'})
    return donations_sum

def sum_funds_by_zip(mec_df, mec_id=None):
    if mec_id is None:
        zip_df = mec_df.groupby(by=['ZIP5']).agg({'Amount':'sum'})
    else:
        cand_df = mec_df[mec_df[' MECID'] == mec_id]
        zip_df = cand_df.groupby(by=['ZIP5']).agg({'Amount':'sum'})
    return zip_df

def base_candidate_fundraising_graph(candidates, mec_df):
    cand_df = sum_funds_by_mecid(mec_df)
    x_values = [ cand_df.loc[candidate.mec_id]['Amount'] for candidate in candidates ]
    y_values = [ candidate.name for candidate in candidates ]

    
    fig = px.bar(x=x_values, y=y_values, template="simple_white", labels={'x':'Candidate Fundraising'})
    # fig.update_layout(yaxis_tickangle=90)
    fig.update_traces(marker_color='rgb(140,190,224)', marker_line_color='rgb(8,47,107)',
                      marker_line_width=1.5, opacity=0.6)
    fig.update_traces(texttemplate='%{y}\n$%{x:.2s}', textposition='inside')
    fig.update_traces(hoverinfo="skip", hovertemplate='$%{x:.2s} <extra>%{y}</extra>')
    fig.update_layout(uniformtext_minsize=12, uniformtext_mode='show')
    fig.update_layout(title_text='Mayoral Candidate Fundraising (2020-2021)')
    basic_graph = dcc.Graph(figure=fig, className="FundraisingBaseGraph", style={"width":"40vw"})

    return basic_graph

def build_zip_amount_geojson(df, mec_id=None):
    if mec_id is None:
        zip_df = df.groupby(by=['ZIP5']).agg({'Amount':'sum'})
    else:
        cand_df = df[df[' MECID'] == mec_id]
        zip_df = cand_df.groupby(by=['ZIP5']).agg({'Amount':'sum'})
    zip_geojson_path = "data/geojson/stl-region-zip_rw.geojson"
    with open(zip_geojson_path) as read_file:
        zip_geojson_data = json.load(read_file)

    for feat in zip_geojson_data['features']:
        if feat['properties']['ZCTA5CE10'] in zip_df.index:
            feat['properties']['Amount'] = zip_df.loc[feat['properties']['ZCTA5CE10']].Amount
        else:
            feat['properties']['Amount'] = 0
    return zip_geojson_data
