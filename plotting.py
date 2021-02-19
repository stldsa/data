import mapping
import contrib
import mec_query

import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
import dash_leaflet as dl 
import dash_leaflet.express as dlx
import dash_core_components as dcc 
import dash_html_components as html

pd.options.plotting.backend = "plotly"

def create_candidate_funds_bar_plot(candidates, mec_df):
    cand_df = contrib.sum_funds_by_mecid(mec_df)

    x_values = []
    y_values = []

    for candidate in candidates:
        if candidate.mec_id in cand_df.index:
            candidate_total = cand_df.loc[candidate.mec_id]['amount']
        else:
            candidate_total = 0
        x_values.append(candidate_total)
        y_values.append(candidate.name)

    bar_color = ['rgb(140,190,224)', 'rgb(22,252,21)', 'rgb(120,10,224)', 'rgb(40,90,24)']
    bar_line_width = 1.5
    bar_line_color = 'rgb(8,47,107)'
    bar_opacity = 0.7

    bar_label_template = '%{y} = $%{x:.3s}'

    fig = px.bar(x=x_values, y=y_values, template="simple_white", labels={'x':'Candidate Fundraising'})
    # Set axes
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(visible=False, showticklabels=False, fixedrange=True)
    # Set traces
    fig.update_traces(marker_color=bar_color, marker_line_width=bar_line_width,
                      marker_line_color=bar_line_color, opacity=bar_opacity,
                      texttemplate=bar_label_template, hoverinfo="skip")
    fig.update_traces(hovertemplate='$%{x:.2s} <extra>%{y}</extra>')

    fig.update_layout(uniformtext_minsize=12, uniformtext_mode='show')
    fig.update_layout(title_text='Mayoral Candidate Fundraising')

    basic_graph = dcc.Graph(
        id="fundraising-graph",
        figure=fig, 
        className="FundraisingBaseGraph", 
        style={"width":"100%"},
        clear_on_unhover=True,
        config={
			'displayModeBar':False,
            # 'staticPlot': True
        }
    )

    return basic_graph

def candidate_funding_details(clicked_name, mec_df):
    funding_detail_box_style = {"margin":"12px", "border":"2px solid black", "padding":"10px", "height":"80%"}
    donation_stats = mec_query.get_contribution_stats_for_candidate(clicked_name)
    return html.Div(children=[
                        html.P([html.Strong("Total monetary donations:"), str(donation_stats["total_collected"])]),
                        html.P([html.Strong("Number of donations:"), str(donation_stats["num_donations"])]),
                        html.P([html.Strong("Average donation:"), str(donation_stats["average_donation"])])
                    ], style=funding_detail_box_style)