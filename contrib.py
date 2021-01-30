import pandas as pd
import plotly.express as px 
import dash_bootstrap_components as dbc
import dash_leaflet as dl 
import dash_core_components as dcc 
import dash_html_components as html




def base_candidate_fundraising_graph(candidates):
    candidate_columns = [
        dbc.Col(html.P(candidate.name), className="candidate") for candidate in candidates
    ]
    dbc.Row(id="candidates-row", children=candidate_columns)
    print(candidates)
    fig = px.bar()
    basic_graph = dcc.Graph(figure=fig)

    return basic_graph


def get_candidate_df():
    
    table_df = pd.read_sql_table(
        "nyc_jobs",
        con=engine,
        schema='public',
        index_col='job_id',
        coerce_float=True,
        columns=[
            'job_id',
            'business_title',
            'job_category',
            'posting_date',
            'posting_updated'
        ],
        parse_dates=[
            'created_at',
            'updated_at'
        ],
        chunksize=500
    )