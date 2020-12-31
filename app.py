import json
import textwrap

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import State, Output, Input
from dash_extensions.javascript import arrow_function

import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

import pandas as pd
import dash_leaflet as dl

elections = pd.read_csv(
    "data/elections/elections.csv", parse_dates=["Date"], index_col="Date"
)
races = pd.read_csv(
    "data/elections/races.csv",
    parse_dates=["Election Date"],
    index_col=["Election Date", "Ballot Item"],
)

ward_data = pd.read_csv(
    "data/elections/ward_data.csv",
    parse_dates=["Election Date"],
    index_col=["Election Date", "Ward"],
)
ward_data["Turnout %"] = 100 * ward_data["Ballots cast"] / ward_data["Reg voters"]

results = pd.read_csv(
    "data/elections/results.csv",
    parse_dates=["Election Date"],
    index_col=["Election Date", "Ward", "Ballot Item", "Ballot Selection"],
)

app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)


side_panel_header = html.Div(
    children="St Louis DSA - Data project",
    style={
        "textAlign": "center",
        "fontWeight": "bold",
        "fontSize": "1.2em",
        "padding": "10px",
        "width": "100%",
        "color": "white",
        "backgroundColor": "red",
    },
)

side_panel_footer_box = html.Div(
    children=[
        html.Div("Labor donated by STL DSA tech committee"),
        html.A(
            "[ Call to action to join DSA ]",
            href="https://dsausa.org/join",
            style={"color": "white", "textDecoration": "italics"},
        ),
    ],
    style={
        "textAlign": "center",
        "textDecoration": "italics",
        "fontSize": "0.8em",
        "padding": "6px",
        "margin": "10px 0",
        "border": "1px dashed white",
    },
)

side_panel_footer = html.Div(
    children=side_panel_footer_box,
    style={
        "width": "100%",
        "color": "white",
        "backgroundColor": "red",
    },
)

# Elections dropdown
# TODO: Automate better (too much of this was by hand)
chosen_election = "nov_2020"  # TODO: figure this out
races_per_election = dict(
    aug_2020=["ag_dem", "rep1_dem", "treas_dem"],  # todo
    nov_2020=["president", "rep1", "prop_d", "prop_1", "prop_r"],
)
election_options = [
    {"label": elections.loc[row, "Name"], "value": row} for row in elections.index
]
election_dropdown = dcc.Dropdown(
    id="election-dropdown",
    options=election_options,
    searchable=False,
    placeholder="Select an election",
)

# Side Panel Form - Put together the form (initially had both an election and race dropdown, just election is cleaner though)
side_panel_form = html.Div(
    children=[election_dropdown],
    id="side-panel-form",
    style={
        "lineHeight": "1.4em",
        "width": "90%",
        "padding": "10px",
        "barderRight": "4px solid red",
    },
)

# Info Panel - This shows the info of the clicked/selected element
info_panel = html.Div(
    [html.Div([], id="ward-info-panel"), html.Div([], id="precinct-info-panel")],
    style={"width": "90%", "height": "70%"},
)

side_panel_layout = html.Div(
    children=[
        side_panel_header,
        side_panel_form,
        info_panel,
        side_panel_footer,
    ],
    id="panel-side",
    style={
        "width": "30%",
        "height": "100vh",
        "maxWidth": "500px",
        "color": "black",
        "backgroundColor": "white",
        "borderRight": "8px solid red",
        "borderLeft": "8px solid red",
        "display": "flex",
        "flexDirection": "column",
        "justifyContent": "space-between",
        "alignItems": "center",
    },
)


# MAP PANEL
# 	Base tile layer
url = "http://{s}.tile.stamen.com/toner-background/{z}/{x}/{y}.png"
attribution = (
    'Map tiles by <a href="http://stamen.com">Stamen Design</a>, '
    'under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. '
    'Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.'
)
base_tile_layer = dl.TileLayer(url=url, attribution=attribution)

# 	Ward overlay
df = pd.read_csv("data/demo/ward_pop.csv")
ward_geojson_path = "data/geojson/stl-city/wards.geojson"
with open(ward_geojson_path) as read_file:
    ward_geojson = json.load(read_file)

wards = dl.GeoJSON(
    data=ward_geojson,  # TODO: Faster is to get PBFs
    options={"style": {"color": "red", "fillOpacity": 0.5, "weight": 2}},
    zoomToBoundsOnClick=True,  # when true, zooms to bounds of feature (e.g. polygon) on click
    hoverStyle=arrow_function(
        dict(weight=4, fillOpacity=0.2, dashArray="")
    ),  # special style applied on hover)
    id="wards-geojson",
)
ward_overlay = dl.Overlay(dl.LayerGroup(wards), name="wards", checked=True)

# 	Wards: Show election info on click
@app.callback(
    Output("ward-info-panel", "children"),
    [Input("wards-geojson", "click_feature")],
    State("election-dropdown", "value"),
)
def ward_click(feature, election_selected):
    div_children = []
    races_contents = []
    if feature is not None:
        ward_num = int(feature["properties"]["Ward"])
        feature_name = html.Div(
            f"Ward {ward_num}",
            style={
                "textAlign": "center",
                "fontSize": "1.6em",
                "fontWeight": "bold",
                "textDecoration": "underline",
            },
        )
        div_children.append(feature_name)
        if election_selected is not None:
            elec_ward_data = ward_data.loc[pd.IndexSlice[election_selected], ward_num]
            turnout = elec_ward_data["Turnout %"]
            div_children.append(
                html.Div(
                    "Turnout: {0:.2f}%".format(turnout),
                    style={"textAlign": "center"},
                )
            )
            # for index, data in df.items():
            # 	print(index, data)
            # #TODO: build up multi layout

            elec_races = races.loc[pd.IndexSlice[election_selected]]

            # prebuild subplots stuff
            subplot_specs = []
            subplot_titles = []
            for race in elec_races.index:
                subplot_specs.append([{"type": "domain"}])
                split_text = "<br>".join(
                    textwrap.wrap(elec_races.loc[race, "Name"], width=21)
                )  # neat little solution for wrapping titles: https://community.plotly.com/t/wrap-long-text-in-title-in-dash/11419
                subplot_titles.append(split_text)
            elec_donuts = make_subplots(
                rows=len(elec_races),
                cols=1,
                specs=subplot_specs,
                subplot_titles=subplot_titles,
            )

            # add traces
            i = 0
            for race in elec_races:
                race = races_per_election[election_selected][race]
                race_name = race["name"]
                race_candidates = race["candidates"]
                race_legendgroup = "a"
                race_pie_layout = go.Layout(
                    title=race_name, showlegend=True, autosize=True
                )
                race_pie_labels = []
                race_pie_counts = []
                remainder = ballots_cast
                for cand in race_candidates:
                    this_cand_vote = df_ward[cand].values[0]
                    race_pie_labels.append(cand)
                    race_pie_counts.append(this_cand_vote)
                    remainder = remainder - this_cand_vote
                if remainder > 0:
                    race_pie_labels.append("No vote / other")
                    race_pie_counts.append(remainder)
                i = i + 1
                elec_donuts.append_trace(
                    go.Pie(
                        labels=race_pie_labels,
                        legendgroup=race_legendgroup,
                        values=race_pie_counts,
                        name=race_name,
                        hole=0.35,
                    ),
                    i,
                    1,
                )

            elec_donuts.update_traces(
                hoverinfo="label+percent",
                textinfo="none",
                textfont_size=15,
                marker={"line": {"color": "#000000", "width": 2}},
            )
            elec_donuts.update(layout_title_text="", layout_showlegend=False)
            elec_donuts.update_layout(height=(i * 240))
            elec_donuts = go.Figure(elec_donuts)
            elec_donuts = px.pie(
                labels="Ballot Selection",
            )
            ward_election_results = dcc.Graph(id="election_pie", figure=elec_donuts)
            div_children.append(html.Br())
            ward_election_results_style = {
                "height": "100%",
                "maxHeight": "380px",
                "overflowY": "scroll",
                "border": "1px solid black",
            }
            div_children.append(
                html.Div(ward_election_results, style=ward_election_results_style)
            )
        else:
            ward_stats = feature["properties"]["extra_data"]
            table_rows = [html.Tr([html.Th("stat"), html.Th("value")])]
            for stat in ward_stats:
                table_rows.append(html.Tr([html.Td(stat), html.Td(ward_stats[stat])]))
            stats_table = html.Table(table_rows)
            stats_container = html.Div(
                stats_table,
                style={
                    "overflowY": "scroll",
                    "maxHeight": "200px",
                    "border": "1px solid",
                },
            )
            div_children.append(html.Br())
            div_children.append(stats_container)
    else:
        # Ward info header
        ward_info_header_style = {"border": "2px dashed", "padding": "8px"}
        div_children.append(
            html.Div(
                children=[
                    html.Em(
                        "(Choose an election and click on a ward to see info about that ward)"
                    )
                ],
                style=ward_info_header_style,
            )
        )
    return html.Div(div_children)
    # Not using this below curruntly
    extra_data = feature["properties"]["extra_data"]

    # TODO: Figure out this, for now I am just doing "stats_container" above
    # Population stacked bar graphs
    trace1 = go.Bar(
        x=["2000 Population", "2010 Population"],
        y=[extra_data["white_pop_2000"], extra_data["white_pop_2010"]],
        name="White",
    )
    trace2 = go.Bar(
        x=["2000 Population", "2010 Population"],
        y=[extra_data["black_pop_2000"], extra_data["black_pop_2010"]],
        name="Black",
    )
    trace3 = go.Bar(
        x=["2000 Population", "2010 Population"],
        y=[
            extra_data["total_pop_2000"]
            - extra_data["black_pop_2000"]
            - extra_data["white_pop_2000"],
            extra_data["total_pop_2010"]
            - extra_data["black_pop_2010"]
            - extra_data["white_pop_2010"],
        ],
        name="Other",
    )
    pop_graph_layout = go.Layout(
        title="Ward population: 2000 -> 2010",
        barmode="stack",
        showlegend=False,
        height=300,
    )
    pop_graph = dcc.Graph(
        id="population_graph",
        figure=go.Figure(data=[trace1, trace2, trace3], layout=pop_graph_layout),
    )
    pop_bar_graph_section = html.Div(children=[pop_graph])

    # Housing pie graphs
    labels = ["Occupied", "Vacant"]
    housing_unit_data_2010 = [
        extra_data["occupied_housing_units_2010"],
        extra_data["vacant_housing_units_2010"],
    ]
    housing_unit_data_2000 = [
        extra_data["occupied_housing_units_2000"],
        extra_data["vacant_housing_units_2000"],
    ]

    housing_pie_layout = go.Layout(
        title="Housing Units", showlegend=False, autosize=True
    )
    housing_pie_2010 = dcc.Graph(
        id="housing_pie_2010",
        figure=go.Figure(
            data=[go.Pie(labels=labels, values=housing_unit_data_2010)],
            layout=housing_pie_layout,
        ),
    )
    housing_pie_2000 = dcc.Graph(
        id="housing_pie_2000",
        figure=go.Figure(
            data=[go.Pie(labels=labels, values=housing_unit_data_2000)],
            layout=housing_pie_layout,
        ),
    )

    housing_pie_graphs_section = html.Div(
        children=[housing_pie_2010, housing_pie_2000],
        style=dict(display="flex", flexDirection="row", width="100%", zIndex=4),
        id="housing_pie_graphs",
    )

    return html.Div(
        [
            f"Ward {feature['properties']['Ward']}:",
            html.Br(),
            pop_bar_graph_section,
            html.Br(),
            housing_pie_graphs_section,
        ],
        style=dict(display="flex", flexDirection="column", width="100%"),
    )


# 	Precinct overlay
pop_by_precinct_path = "data/demo/precinct_pop.csv"
df = pd.read_csv(pop_by_precinct_path)
precinct_geojson_path = "data/geojson/stl-city/precincts.geojson"
with open(precinct_geojson_path) as read_file:
    precinct_geojson = json.load(read_file)
    for precinct_object in precinct_geojson["features"]:
        df_precinct = df.loc[
            df["HANDLE"] == int(precinct_object["properties"]["HANDLE"])
        ]
        precinct_object["properties"]["extra_data"] = dict(
            est_white=int(df_precinct.values[0][3]),
            est_black=int(df_precinct.values[0][4]),
        )
precincts = dl.GeoJSON(
    data=precinct_geojson,
    options=dict(style=dict(color="purple", fillOpacity=0.5)),
    zoomToBoundsOnClick=True,
    hoverStyle=arrow_function(dict(weight=4, fillOpacity=0.2, dashArray="")),
    id="precincts-geojson",
)
precinct_overlay = dl.Overlay(precincts, name="precincts", checked=False)

# 	Precincts: Show est white and black pops on click
@app.callback(
    Output("precinct-info-panel", "children"),
    [Input("precincts-geojson", "hover_feature")],
)
def precinct_click(feature):
    if feature is not None:
        return html.Div(
            # I do not know what data these estimates are derived from, but they were the only precinct level data I had handy
            [
                f"Ward {feature['properties']['WARD10']}, Precinct {feature['properties']['PREC10']}:",
                html.Br(),
                f"Estimated black pop: {feature['properties']['extra_data']['est_black']}",
                html.Br(),
                f"Estimated white pop: {feature['properties']['extra_data']['est_white']}",
            ]
        )


# 	Neighborhood overlay
df = pd.read_csv(pop_by_precinct_path)
neighborhodd_geojson_path = "data/geojson/stl-city/neighborhoods.geojson"
with open(neighborhodd_geojson_path) as read_file:
    neighborhodd_geojson = json.load(read_file)
precincts = dl.GeoJSON(
    data=neighborhodd_geojson,
    options=dict(style=dict(color="green")),
    zoomToBoundsOnClick=True,
    hoverStyle=arrow_function(dict(weight=4, fillOpacity=0.2, dashArray="")),
    id="neighborhoods-geojson",
)
neighborhood_overlay = dl.Overlay(precincts, name="neighborhood", checked=False)

# 	Map and wrapper
city_map = html.Div(
    children=[
        dl.Map(
            dl.LayersControl(
                [base_tile_layer, ward_overlay, precinct_overlay, neighborhood_overlay]
            ),
            zoom=12,
            center=[38.648, -90.253],
            style={
                "width": "100%",
                "height": "100vh",
                "margin": "none",
                "display": "block",
            },
        )
    ],
    id="city-map-wrapper",
)

# 	Main layout component for the map
map_panel_layout = html.Div(
    id="map-panel",
    children=[city_map],
    style={"width": "100%", "height": "100vh", "display": "block"},
)

# ROOT
root_layout = html.Div(
    id="root",
    children=[side_panel_layout, map_panel_layout],
    style={"display": "flex", "flexDirection": "row", "margin": 0},
)

app.layout = root_layout

if __name__ == "__main__":
    app.run_server(debug=True)
