import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd

import mapping, plotting, mec_query
from mec_query import Candidate, Contributor, Contribution

import locale

locale.setlocale(locale.LC_ALL, "en_US.UTF-8")


def get_error_404(pathname):
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognized"),
        ]
    )


fundraising_classes = [0, 100, 500, 1000, 2000, 5000, 10000, 20000]
fundraising_colorscale = [
    "#FFEDA0",
    "#FED976",
    "#FEB24C",
    "#FD8D3C",
    "#FC4E2A",
    "#E31A1C",
    "#BD0026",
    "#800026",
]
fundraising_style = {
    "weight": 2,
    "opacity": 1,
    "color": "white",
    "dashArray": 3,
    "fillOpacity": 0.7,
}
fundraising_ctg = [
    "${}+".format(cls, fundraising_classes[i + 1])
    for i, cls in enumerate(fundraising_classes[:-1])
] + ["${}+".format(fundraising_classes[-1])]


def build_choropleth_hideout(color_prop):
    hideout = dict(
        colorscale=fundraising_colorscale,
        classes=fundraising_classes,
        style=fundraising_style,
        colorProp=color_prop,
    )
    return hideout


def get_side_panel_header():
    # Side panel header
    side_panel_header_style = {
        "textAlign": "center",
        "fontWeight": "bold",
        "fontSize": "1.2em",
        "padding": "10px",
        "width": "100%",
        "color": "white",
        "backgroundColor": "red",
    }
    side_panel_header = html.Div(
        children="St Louis DSA - Open Data project", style=side_panel_header_style
    )
    return side_panel_header


def get_side_panel_intro():
    side_panel_intro_style = {
        "padding": "40px 20px",
        "fontSize": "1em",
        "lineHeight": "1.13em",
    }
    stldsa_link_style = {"color": "red", "fontWeight": "bold", "font": "Roboto"}
    side_panel_intro = html.Div(
        children=[
            html.Strong("On March 2,"),
            " St Louis City will have primary elections for several offices, including mayor and more than half of the Board of Aldermen.",
            html.Br(),
            html.Br(),
            html.A("St Louis DSA ", href="https://stldsa.org", style=stldsa_link_style),
            " is proud to provide this tool to the voters of St Louis. You can use the options below to view campaign contributions for our mayoral candidates. We hope that in democratizing access to this information, voters will be best able to decide who they would like to represent them.",
            # html.Br(), html.Br(),
            # html.Em("Full disclosure: St Louis DSA has endorsed Megan Green for 15th Ward Alder.")
        ],
        style=side_panel_intro_style,
    )
    return side_panel_intro


def get_selected_layer_buttons():
    button_group = dbc.ButtonGroup([
        dbc.Button("Voter precincts", id="precinct-button", active=True, color="light", outline=True, className="mr-1"),
        dbc.Button("Neighborhoods / Municipalities", id="neighborhood-button", color="light", outline=True, className="mr-1"),
        dbc.Button("ZIP Codes", id="zip-button", color="light", outline=True, className="mr-1"),
    ], size="md", className="mr-1", id="select-layer")
    return button_group

def get_select_layer_section():
    select_layer_section_style = {
        "backgroundColor": "red",
        "color": "white",
        "padding": "10px 0",
        "width": "100%",
        "textAlign": "center"
    }
    return html.Div([
        get_selected_layer_buttons()
    ], style=select_layer_section_style)
	
# Currently used for handling candidates
def get_side_panel_layout(df):
    side_panel_style = {
        "flexShrink": 0,
        "color": "black",
        "backgroundColor": "white",
        "borderRight": "8px solid red",
        "borderLeft": "8px solid red",
        "display": "flex",
        "flexDirection": "column",
        "justifyContent": "flex-start",
        "alignItems": "center",
    }
    side_panel_layout = html.Div(
        children=[
            get_side_panel_header(),
            html.Div([
                get_side_panel_intro(),
                get_side_panel_form(df),
            ], style={"height":"100%", "overflowY":"auto"}),
            # get_candidate_select(candidates),
            # reset_selection_button(),
            # side_panel_form,
            # get_expand_button(),
            # html.Div([
            #     html.Strong("CURRENT VIEW:"),
            #     "Total contributions in each ",
            #     html.Span("precinct", id="base-layer-name"),
            #     " for ",
            #     html.Span("all candidates", id="candidate-name-span")
            # ], style={"width": "90%"}),
            get_select_layer_section(),
            get_side_panel_footer(),
        ],
        className="SidePanel_NotExpanded",
        id="panel-side",
        style=side_panel_style,
    )
    return side_panel_layout


def get_collapse_candidate_info():
    return dbc.Collapse(id="candidate_info_collapse")


def get_candidate_info_card(candidate):
    if candidate is not None:
        donation_stats = mec_query.get_contribution_stats_for_candidate(candidate.name)

        return dbc.Card(
            children=[
                dbc.CardHeader(f"Donation summary for {candidate.name}"),
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        "Total # of Donations:",
                                        html.Br(),
                                        str(donation_stats["num_donations"]),
                                    ]
                                ),
                                dbc.Col(
                                    [
                                        "Mean Donation:",
                                        html.Br(),
                                        locale.currency(
                                            donation_stats["average_donation"],
                                            grouping=True,
                                        ),
                                    ]
                                ),
                                dbc.Col(["Histogram (?)", html.Br(), "other info?"]),
                            ]
                        )
                    ]
                ),
            ]
        )
    else:
        return None


def get_side_panel_form(df):
    return html.Div(
        children=[
            plotting.sidebar_graph_component(
                plotting.create_candidate_funds_bar_plot(df),
            ),
            dbc.Collapse(children=[], id="candidate_info_collapse"),
        ],
        id="side-panel-form",
        style={"width": "90%", "flexGrow": 4, },
    )


def get_side_panel_footer():
    # Side panel footer
    side_panel_footer_box_style = {
        "textAlign": "center",
        "textDecoration": "italics",
        "fontSize": "0.8em",
        "padding": "6px",
        "margin": "10px 0",
        "border": "1px dashed white",
    }
    side_panel_footer_box = html.Div(
        children=[
            html.Div("Labor donated by STL DSA tech committee"),
            html.A(
                "[ Call to action to join DSA ]",
                href="https://dsausa.org/join",
                style={"color": "white", "textDecoration": "italics"},
            ),
        ],
        style=side_panel_footer_box_style,
    )
    side_panel_footer_style = {
        "width": "100%",
        "color": "white",
        "backgroundColor": "red",
        "marginTop": "auto"
    }
    side_panel_footer = html.Div(
        children=side_panel_footer_box, style=side_panel_footer_style
    )
    return side_panel_footer


def get_sidebar_layout(db):
    candidates_df = pd.read_sql(db.session.query(Candidate).statement, db.session.bind)
    candidates_df["$ Raised"] = candidates_df['name'].apply(mec_query.get_candidate_total_donations)
    candidates_df = candidates_df.rename(columns={"name": "Candidate"})
    mec_ids = ["C201499", "C201099", "C201500", "C211544"]
    # df = pd.read_sql(db.session.query(Contribution).statement, db.session.bind)
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(get_side_panel_layout(candidates_df), md=5, lg=4),
                    dbc.Col(mapping.get_map_panel_layout(), md=7, lg=8),
                ],
                no_gutters=True,
            )
        ],
        fluid=True,
        className="remove-padding",
    )


def get_floatbox_card_contents(id_suffix, header_text="", body_contents=[]):
    header_style = {"fontSize": "1.5em", "fontWeight": "bold"}
    header_span = html.Span(header_text, style=header_style)
    close_card_button = dbc.Button(
        " X ",
        outline=True,
        color="danger",
        id="card-box-close-" + id_suffix,
        style={"float": "right"},
    )
    return [
        dbc.CardHeader([header_span, close_card_button]),
        dbc.CardBody(body_contents),
    ]


def get_zip_click_card(feature):
    header_style = {"fontSize": "1.5em", "fontWeight": "bold"}

    if feature is not None:
        header_text = html.Span(
            f"ZIP Code {feature['properties']['ZCTA5CE10']}", style=header_style
        )
        body_contents = [
            html.Strong("Total funds contributed for Mayor's race (all candidates): "),
            html.Span(
                locale.currency(
                    feature["properties"]["total_mayor_donations"], grouping=True
                )
            ),
        ]
    else:
        header_text = html.Span(f"No ZIP Selected")
        body_contents = [html.Em("No info to display")]

    card_content = [
        dbc.CardHeader(
            [
                header_text,
                dbc.Button(
                    " X ",
                    outline=True,
                    color="danger",
                    id="zip-box-close",
                    style={"float": "right"},
                ),
            ]
        ),
        dbc.CardBody(body_contents),
    ]

    zip_card = dbc.Card(card_content, color="dark", outline=True, id="floatbox")
    return zip_card
