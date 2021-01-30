import json
import contrib

import dash_leaflet as dl 
import dash_core_components as dcc 
import dash_html_components as html
import dash_bootstrap_components as dbc

# Currently used for handling candidates
def get_side_panel_layout(candidates):
    side_panel_style={"width": "40%", "height": "100vh", "maxWidth":"500px",
        "color": "black", "backgroundColor": "white", "borderRight": "8px solid red", "borderLeft": "8px solid red",
        "display":"flex", "flexDirection":"column", "justifyContent":"space-between", "alignItems":"center"}
    side_panel_layout = html.Div(
        children=[
            get_side_panel_header(),
            get_side_panel_intro(),
            get_side_panel_form(candidates),
            # side_panel_form,
            # info_panel,
            get_side_panel_footer()
        ],
        id='panel-side',
        style=side_panel_style
    )
    return side_panel_layout

def get_side_panel_header():
    # Side panel header
    side_panel_header_style = {"textAlign":"center", "fontWeight":"bold", "fontSize":"1.2em", 
        "padding":"10px", "width":"100%",
        "color": "white", "backgroundColor": "red"}
    side_panel_header = html.Div(children="St Louis DSA - Data project", style=side_panel_header_style)
    return side_panel_header

def get_side_panel_intro():
    side_panel_intro_style = {"padding":"12px", "fontSize":"1em", "lineHeight":"1.13em"}
    stldsa_link_style = {"color":"red", "fontWeight":"bold", "font":"Roboto"}
    side_panel_intro = html.Div(children=[
        html.Strong("On March 2,"),
        " St Louis City will have primary elections for several offices, including mayor and more than half of the Board of Aldermen.",
        html.Br(), html.Br(),
        html.A("St Louis DSA ", href="https://stldsa.org", style=stldsa_link_style),
        " is proud to provide this tool to the voters of St Louis. You can use the options below to view campaign contributions for our mayoral candidates. We hope that in democratizing access to this information, voters will be best able to decide who they would like to represent them.",
        html.Br(), html.Br(),
        html.Em("Full disclosure: St Louis DSA has endorsed _________")
    ], style=side_panel_intro_style)
    return side_panel_intro

def get_side_panel_footer():
    # Side panel footer
    side_panel_footer_box_style = {"textAlign":"center", "textDecoration":"italics", "fontSize":"0.8em", 
        "padding":"6px", "margin":"10px 0", "border":"1px dashed white"}
    side_panel_footer_box = html.Div(children=[
        html.Div("Labor donated by STL DSA tech committee"),
        html.A("[ Call to action to join DSA ]", href="https://dsausa.org/join", style={"color":"white","textDecoration":"italics"})
    ], style=side_panel_footer_box_style)
    side_panel_footer_style = {"width":"100%", "color": "white", "backgroundColor": "red"}
    side_panel_footer = html.Div(children=side_panel_footer_box, style=side_panel_footer_style)
    return side_panel_footer

def get_side_panel_form(candidates):
    basic_graph = contrib.base_candidate_fundraising_graph(candidates)
    side_panel_form = html.Div(children=[
        basic_graph
    ])
    return side_panel_form


def get_map_panel_layout():
    stl_center = [38.648, -90.253]
    city_map_style = {"width": "100%", "height": "100vh", "margin": "none", "display": "block"}
    city_map = html.Div(
        children=[
            dl.Map(
                dl.LayersControl(children=[
                    get_base_toner_tile_layer(), 
                #    ward_overlay, 
                    get_precinct_overlay(), 
                #    neighborhood_overlay
                ]),
                zoom=12, 
                center=stl_center, 
                style=city_map_style
            )
        ],
        id='city-map-wrapper',
    )

    map_panel_style = {'width': '100%', 'height': '100vh', "display": "block"}
    map_panel = html.Div(
        id='map-panel',
        children=[
            city_map
        ], 
        style=map_panel_style
    )
    return map_panel

def get_precinct_overlay():
    precinct_geojson_path = "data/geojson/stl-city/precincts.geojson"
    with open(precinct_geojson_path) as read_file:
        precinct_geojson = json.load(read_file)
    precincts = dl.GeoJSON(data=precinct_geojson,
					options=dict(style=dict(color="purple", fillOpacity=0.5)),
					zoomToBoundsOnClick=True,
					# hoverStyle=arrow_function(dict(weight=4, fillOpacity=0.2, dashArray='')),
					id="precincts-geojson")
    precinct_overlay = dl.Overlay(precincts, name="precincts", checked=True)
    return precinct_overlay


def get_base_toner_tile_layer():
    # 	Base tile layer
    url = "http://{s}.tile.stamen.com/toner-background/{z}/{x}/{y}.png"
    attribution = (
        'Map tiles by <a href="http://stamen.com">Stamen Design</a>, '
        'under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. '
        'Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.'
    )
    base_tile_layer = dl.TileLayer(url=url, attribution=attribution)
    return base_tile_layer


