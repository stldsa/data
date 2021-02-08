import mapping
import contrib

import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
import dash_leaflet as dl 
import dash_leaflet.express as dlx
import dash_core_components as dcc 
import dash_html_components as html

pd.options.plotting.backend = "plotly"

def create_candidate_funds_bar_plot(candidates, mec_df):
    cand_df = sum_funds_by_mecid(mec_df)
    x_values = [ candidate.df.loc[candidate.mec_id]['amount'] for candidate in candidates ]
    y_values = [ candidate.name for candidate in candidates ]

    bar_color = 'rgb(140,190,224)'
    bar_line_width = 1.5
    bar_line_color = 'rgb(8,47,107)'
    bar_opacity = 0.7

    bar_label_template = '%{y} = $%{x:.3s}'

    fig = px.bar(x=x_values, y=y_values, template="simple_white")
    # Set axes
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(visible=False, showticklabels=False, fixedrange=True)
    # Set traces
    fig.update_traces(marker_color=bar_color, marker_line_width=bar_line_width,
                      marker_line_color=bar_line_color, opacity=bar_opacity,
                      texttemplate=bar_label_template, hoverinfo="skip")
    return fig 