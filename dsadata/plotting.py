from dsadata import mapping, mec_query, db
from dsadata.mec_query import Candidate, Contribution, Contributor
from sqlalchemy import and_
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import dash_leaflet.express as dlx
import dash_core_components as dcc
import dash_html_components as html


pd.options.plotting.backend = "plotly"

candidate_df = pd.read_csv("dsadata/static/candidates_2021-03-02.csv")


def parse_geography_properties_for_fundraising(geography_properties, mec_id):
    return geography_properties["mec_donations_" + mec_id + "_with_pacs"]


def get_candidate_colors(contest_candidates_df):
    colors = [
        "#66c2a5",
        "#fc8d62",
        "#8da0cb",
        "#e78ac3",
        "#a6d854",
        "#ffd92f",
        "#e5c494",
        "#b3b3b3",
    ]
    color_map = {}
    contest_candidates_df = contest_candidates_df.sort_values(
        "Candidate Name"
    ).reset_index()
    for index, row in contest_candidates_df.iterrows():
        candidate_name = row["Candidate Name"]
        color_map[candidate_name] = colors[index]
    return color_map


def create_candidate_funds_pie(contest, geography_properties):

    contest_name = mec_query.get_standard_contest_name(contest)

    contest_candidates_df = candidate_df[candidate_df["Office Sought"] == contest]
    contest_candidates_df.loc[:, "Fundraising"] = contest_candidates_df.apply(
        lambda x: parse_geography_properties_for_fundraising(
            geography_properties, x["MECID"]
        ),
        axis=1,
    )
    color_discrete_map = get_candidate_colors(contest_candidates_df)
    fig = px.pie(
        contest_candidates_df,
        values="Fundraising",
        color="Candidate Name",
        names="Candidate Name",
        hover_name="Candidate Name",
        color_discrete_map=get_candidate_colors(contest_candidates_df),
        hole=0.3,
        width=250,
        height=250,
    )
    fig.update_traces(
        textinfo="none",
        hovertemplate="<b>%{label}</b><br>Funds raised here: $%{value}",
        automargin=True,
    )
    fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=10, b=10))

    pie_graph = dcc.Graph(
        id="geography-pie-graph",
        figure=fig,
        config={
            "displayModeBar": False,
            # 'staticPlot': True
        },
    )
    return html.Div([pie_graph], style={"width": "250px", "margin": "auto"})


def create_candidate_funds_bar_plot(candidates_df):
    df = candidates_df
    fig = px.bar(
        df,
        x="$ Raised",
        y="Candidate",
        template="simple_white",
    )
    bar_color = [
        "rgb(140,190,224)",
        "rgb(22,252,21)",
        "rgb(120,10,224)",
        "rgb(40,90,24)",
    ]
    bar_line_width = 1.5
    bar_line_color = "rgb(8,47,107)"
    bar_opacity = 0.7

    bar_label_template = "%{y}"
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(visible=False, showticklabels=False, fixedrange=True)
    # Set traces
    fig.update_traces(
        marker_color=bar_color,
        marker_line_width=bar_line_width,
        marker_line_color=bar_line_color,
        opacity=bar_opacity,
        texttemplate=bar_label_template,
        hoverinfo="skip",
    )
    fig.update_traces(hovertemplate="$%{x:.2s} <extra>%{y}</extra>")

    fig.update_layout(uniformtext_minsize=12, uniformtext_mode="show")
    fig.update_layout(title_text="Mayoral Candidate Fundraising")
    fig.update_yaxes(categoryorder="total ascending")

    return fig


def sidebar_graph_component():
    graph_component = dcc.Graph(
        id="fundraising-graph",
        # figure=fig,
        className="FundraisingBaseGraph",
        style={"width": "100%"},
        clear_on_unhover=True,
        config={
            "displayModeBar": False,
            # 'staticPlot': True
        },
    )
    return graph_component


def build_candidate_info_graph(mec_id):
    this_candidate = candidate_df.loc[candidate_df["MECID"] == mec_id]
    candidate_name = this_candidate["Candidate Name"].item()
    contribution_df = pd.read_sql(
        db.session.query(Contribution).filter("MECID" == mec_id).statement,
        db.session.bind,
    )
    return html.Div(["Info on " + candidate_name])


def build_contest_info_graph(contest):
    contest_candidates_df = candidate_df[candidate_df["Office Sought"] == contest]
    contest_mec_ids = contest_candidates_df["MECID"].unique()
    candidate_color_map = get_candidate_colors(contest_candidates_df)
    contribution_df = pd.read_sql(
        db.session.query(Contribution)
        .filter(
            and_(
                # Contribution.lat != "Nan",
                Contribution.mec_id.in_(contest_mec_ids)
            )
        )
        .statement,
        db.session.bind,
    )
    return html.Div(["Info on " + contest])


# def create_candidate_funds_bar_plot(candidates, mec_df):
#     cand_df = contrib.sum_funds_by_mecid(mec_df)

#     x_values = []
#     y_values = []

#     for candidate in candidates:
#         if candidate.mec_id in cand_df.index:
#             candidate_total = cand_df.loc[candidate.mec_id]['amount']
#         else:
#             candidate_total = 0
#         x_values.append(candidate_total)
#         y_values.append(candidate.name)

#     bar_color = ['rgb(140,190,224)', 'rgb(22,252,21)', 'rgb(120,10,224)', 'rgb(40,90,24)']
#     bar_line_width = 1.5
#     bar_line_color = 'rgb(8,47,107)'
#     bar_opacity = 0.7

#     bar_label_template = '%{y} = $%{x:.3s}'

#     fig = px.bar(x=x_values, y=y_values, template="simple_white", labels={'x':'Candidate Fundraising'})
#     # Set axes
#     fig.update_xaxes(fixedrange=True)
#     fig.update_yaxes(visible=False, showticklabels=False, fixedrange=True)
#     # Set traces
#     fig.update_traces(marker_color=bar_color, marker_line_width=bar_line_width,
#                       marker_line_color=bar_line_color, opacity=bar_opacity,
#                       texttemplate=bar_label_template, hoverinfo="skip")
#     fig.update_traces(hovertemplate='$%{x:.2s} <extra>%{y}</extra>')

#     fig.update_layout(uniformtext_minsize=12, uniformtext_mode='show')
#     fig.update_layout(title_text='Mayoral Candidate Fundraising')

#     basic_graph = dcc.Graph(
#         id="fundraising-graph",
#         figure=fig,
#         className="FundraisingBaseGraph",
#         style={"width":"100%"},
#         clear_on_unhover=True,
#         config={
# 			'displayModeBar':False,
#             # 'staticPlot': True
#         }
#     )

#     return basic_graph


def candidate_funding_details(clicked_name, mec_df):
    funding_detail_box_style = {
        "margin": "12px",
        "border": "2px solid black",
        "padding": "10px",
        "height": "80%",
    }
    donation_stats = mec_query.get_contribution_stats_for_candidate(clicked_name)
    return html.Div(
        children=[
            html.P(
                [
                    html.Strong("Total monetary donations:"),
                    str(donation_stats["total_collected"]),
                ]
            ),
            html.P(
                [
                    html.Strong("Number of donations:"),
                    str(donation_stats["num_donations"]),
                ]
            ),
            html.P(
                [
                    html.Strong("Average donation:"),
                    str(donation_stats["average_donation"]),
                ]
            ),
        ],
        style=funding_detail_box_style,
    )
