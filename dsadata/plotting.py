from dsadata import mec_query, db
from dsadata.mec_query import Contribution
from sqlalchemy import and_
import pandas as pd
import plotly.express as px
import dash_core_components as dcc

import dash_html_components as html


pd.options.plotting.backend = "plotly"

candidate_df = pd.read_sql("candidate", db.engine)


def parse_geography_properties_for_fundraising(geography_properties, mec_id):
    return geography_properties["mec_donations_" + mec_id + "_with_pacs"]


def get_candidate_colors(contest_candidates_df, col_name):
    colors = ["#1b9e77", "#d95f02", "#7570b3", "#e7298a", "#66a61e", "#e6ab02"]
    color_map = {}
    contest_candidates_df = contest_candidates_df.sort_values(col_name).reset_index()
    for index, row in contest_candidates_df.iterrows():
        candidate_name = row[col_name]
        color_map[candidate_name] = colors[index]
    return color_map


def create_candidate_funds_pie(contest, geography_properties):

    contest_name = mec_query.get_standard_contest_name(contest)
    contest_candidates_df = candidate_df[candidate_df["Office Sought"] == contest]
    contest_candidates_df["Candidate Name"] = contest_candidates_df[
        "Candidate Name"
    ].str.title()
    contest_candidates_df.loc[:, "Fundraising"] = contest_candidates_df.apply(
        lambda x: parse_geography_properties_for_fundraising(
            geography_properties, x["MECID"]
        ),
        axis=1,
    )
    color_discrete_map = get_candidate_colors(contest_candidates_df, "Candidate Name")
    fig = px.pie(
        contest_candidates_df,
        values="Fundraising",
        color="Candidate Name",
        names="Candidate Name",
        hover_name="Candidate Name",
        color_discrete_map=color_discrete_map,
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
        className="FundraisingBaseGraph",
        style={"width": "100%"},
        clear_on_unhover=True,
        config={
            "displayModeBar": False,
        },
    )
    return graph_component


def build_candidate_info_graph(mec_id):
    this_candidate = candidate_df.loc[candidate_df["MECID"] == mec_id]
    candidate_name = this_candidate["Candidate Name"].item()
    return html.Div(["Info on " + candidate_name])


def build_contest_info_graph(contest):
    contest_candidates_df = candidate_df[candidate_df["Office Sought"] == contest]
    contest_candidates_df["Candidate Name"] = contest_candidates_df[
        "Candidate Name"
    ].str.title()
    candidate_mec_ids = contest_candidates_df["MECID"].unique()
    candidate_color_map = get_candidate_colors(contest_candidates_df, "Candidate Name")
    if contest == "Mayor - City of St. Louis":
        candidate_pac_dict = mec_query.candidate_pac_dict
    else:
        candidate_pac_dict = {}
    candidate_pac_df = pd.DataFrame.from_dict(candidate_pac_dict, orient="index")
    candidate_pac_df = candidate_pac_df.rename(columns={"PAC Name": "Committee Name"})
    candidate_pac_df["Committee Type"] = "PAC"

    contest_candidates_df = contest_candidates_df.set_index("MECID")
    contest_candidates_df["Committee Type"] = "Candidate Committee"

    all_contest_mec_df = pd.concat([contest_candidates_df, candidate_pac_df])
    contest_mec_ids = all_contest_mec_df.index.values

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
    contribution_df = contribution_df.merge(
        all_contest_mec_df, left_on=" MECID", right_on="Candidate MECID"
    )
    print(contribution_df["Candidate Name"])
    totals_df = contribution_df.groupby(
        ["Candidate Name", "Committee Name"], as_index=False
    ).agg({"Amount": "sum", "Committee Type": "first"})
    totals_df = pd.concat([totals_df, all_contest_mec_df], copy=False)
    fig = px.bar(
        totals_df,
        y="Candidate Name",
        x="Amount",
        orientation="h",
        template="simple_white",
        color="Candidate Name",
        color_discrete_map=candidate_color_map,
        barmode="stack",
        custom_data=["Committee Type", "Committee Name"],
    )
    fig.update_layout(
        showlegend=False,
    )
    fig.update_xaxes(fixedrange=True, title_text="Funds raised")
    fig.update_yaxes(visible=True, showline=True, fixedrange=True, title_text="")
    fig.update_traces(
        marker_line_width=1.5,
        hovertemplate="<b>%{customdata[1]}</b><br><i>(%{customdata[0]})</i><br><b>Funds raised: </b>$%{x:.3s}<extra></extra>",
    )

    bar_label_template = "%{y} = $%{x:.3s}"

    graph_component = dcc.Graph(
        id="contest-fundraising-graph",
        figure=fig,
        style={"width": "100%"},
        config={
            "displayModeBar": False,
        },
    )

    return html.Div(
        [
            graph_component,
            html.Div(
                [
                    html.Em(
                        "(Candidate committees that neither recieve nor expend over $500 are not required to report details on their campaign finance)"
                    )
                ],
                style={
                    "fontSize": ".9em",
                    "lineHeight": "1em",
                    "paddingBottom": "10px",
                },
            ),
        ]
    )


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
