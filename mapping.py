import json
import contrib

import geopandas as gpd

import dash_leaflet as dl 
import dash_leaflet.express as dlx
import dash_core_components as dcc 
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash_extensions.javascript import arrow_function, Namespace
import dash_daq as daq

import plotting

import plotly.express as px

# Currently used for handling candidates
def get_side_panel_layout(candidates, df):
    side_panel_style={"height": "100vh", "flexShrink":0,
        "color": "black", "backgroundColor": "white", "borderRight": "8px solid red", "borderLeft": "8px solid red",
        "display":"flex", "flexDirection":"column", "justifyContent":"flex-start", "alignItems":"center"}
    side_panel_layout = html.Div(
        children=[
            get_side_panel_header(),
            get_side_panel_intro(),
            get_side_panel_form(candidates, df),
            # get_candidate_select(candidates),
            # reset_selection_button(),
            # side_panel_form,;
            # info_panel,
            # get_expand_button(),
            get_side_panel_footer()
        ],
        className='SidePanel_NotExpanded',
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
    side_panel_intro_style = {"padding":"40px 20px", "fontSize":"1em", "lineHeight":"1.13em"}
    stldsa_link_style = {"color":"red", "fontWeight":"bold", "font":"Roboto"}
    side_panel_intro = html.Div(children=[
        html.Strong("On March 2,"),
        " St Louis City will have primary elections for several offices, including mayor and more than half of the Board of Aldermen.",
        html.Br(), html.Br(),
        html.A("St Louis DSA ", href="https://stldsa.org", style=stldsa_link_style),
        " is proud to provide this tool to the voters of St Louis. You can use the options below to view campaign contributions for our mayoral candidates. We hope that in democratizing access to this information, voters will be best able to decide who they would like to represent them.",
        html.Br(), html.Br(),
        html.Strong("Hover over or click the bar graph below to get started:"),
        # html.Br(), html.Br(),
        # html.Em("Full disclosure: St Louis DSA has endorsed Megan Green for 15th Ward Alder.")
    ], style=side_panel_intro_style)
    return side_panel_intro

def get_expand_button():
    expand_button = daq.ToggleSwitch(size=50, id='expand-side-swith')  
    return expand_button

def get_side_panel_footer():
    # Side panel footer
    side_panel_footer_box_style = {"textAlign":"center", "textDecoration":"italics", "fontSize":"0.8em", 
        "padding":"6px", "margin":"10px 0", "border":"1px dashed white"}
    side_panel_footer_box = html.Div(children=[
        html.Div("Labor donated by STL DSA tech committee"),
        html.A("[ Call to action to join DSA ]", href="https://dsausa.org/join", style={"color":"white","textDecoration":"italics"})
    ], style=side_panel_footer_box_style)
    side_panel_footer_style = {"width":"100%", "color": "white", "backgroundColor": "red", "align-self":"flex-end"}
    side_panel_footer = html.Div(children=side_panel_footer_box, style=side_panel_footer_style)
    return side_panel_footer

def get_candidate_select(candidates):
    selection = dcc.RadioItems(
        id='candidate-select', 
        options=[{'value': c.mec_id, 'label': c.name} 
                 for c in candidates],
        value=candidates[0].mec_id,
        labelStyle={'display': 'inline-block'},
        className='candidateSelect'
    )
    return selection 

def reset_selection_button():
    reset_button = html.Button('Reset', id='reset-candidate-button')
    return reset_button

def get_side_panel_form(candidates, df):
    return html.Div(children=[plotting.create_candidate_funds_bar_plot(candidates, df)],
                    id="side-panel-form", style={'width':'100%', 'flexGrow': 4})

def get_map_panel_zip_layout():
    classes = [0, 100, 500, 1000, 2000, 5000, 10000, 20000]
    colorscale = ['#FFEDA0', '#FED976', '#FEB24C', '#FD8D3C', '#FC4E2A', '#E31A1C', '#BD0026', '#800026']
    style = {"weight":2, "opacity":1, "color":"white", "dashArray":3, "fillOpacity":0.7}

    ctg = ["{}+".format(cls, classes[i + 1]) for i, cls in enumerate(classes[:-1])] + ["{}+".format(classes[-1])]
    colorbar = dlx.categorical_colorbar(categories=ctg, colorscale=colorscale, width=400, height=30, position="bottomright")

    ns = Namespace("dlx", "choropleth")
    zip_geojson = dl.GeoJSON(data=None,  # url to geojson file
                        options=dict(style=ns("style")),  # how to style each polygon
                        zoomToBounds=False,  # when true, zooms to bounds when data changes (e.g. on load)
                        zoomToBoundsOnClick=True,  # when true, zooms to bounds of feature (e.g. polygon) on click
                        hoverStyle=arrow_function(dict(weight=5, color='#666', dashArray='')),  # style applied on hover
                        hideout=dict(colorscale=colorscale, classes=classes, style=style, colorProp="Amount"),
                        id="zips-geojson")

    stl_center = [38.648, -90.253]
    city_map_style = {"height": "100vh", "margin": "none", "display": "block"}
    city_map = html.Div(
        dl.Map(children=[get_base_toner_tile_layer(), zip_geojson, colorbar], zoom=12, center=stl_center), 
        style=city_map_style, id="map")
    map_panel_style = {'width': '100%', 'height': '100vh', "display": "block"}
    map_panel = html.Div(id='map-panel',
        children=city_map, style=map_panel_style)
    return map_panel

def get_precinct_overlay():
    # original file was wrong hand rule, whis one was rewound with geojson-rewind:
    precinct_geojson_path = "data/geojson/stl-city/precincts_rw.geojson"
    with open(precinct_geojson_path) as read_file:
        precinct_geojson = json.load(read_file)
    precincts = dl.GeoJSON(data=precinct_geojson,
					options=dict(style=dict(color="blue", fillOpacity=0.5)),
					zoomToBoundsOnClick=True,
					hoverStyle=arrow_function(
                        dict(weight=4, fillOpacity=0.2, dashArray="")
                    ),
					id="precincts-geojson")
    precinct_overlay = dl.Overlay(precincts, name="precincts", checked=False)
    return precinct_overlay

def get_zip_overlay(mec_df, candidate):
    if candidate is not None:
        cand_df = contrib.sum_funds_by_zip(cand_zip_df)
    else:
        df = cand_zip_df[cand_zip_df[' MECID'] == candidate] 
    # original file was wrong hand rule, whis one was rewound with geojson-rewind:
    zip_geojson_path = "data/geojson/stl-region-zip_rw.geojson"
    gdf = gpd.read_file(zip_geojson_path)
    gdf = gdf.merge(cand_zip_df, left_on="ZCTA5CE10", right_on="ZIP5")
    if candidate is not None:
        df = contrib.sum_funds_by_zip(cand_zip_df)
    else:
        df = cand_zip_df[cand_zip_df[' MECID'] == candidate]
    with open(zip_geojson_path) as read_file:
        zip_geojson = json.load(read_file)
    zips = dl.GeoJSON(data=zip_geojson,
                    options=dict(style=dict(color="purple", fillOpacity=0.5)),
                    zoomToBoundsOnClick=True,
                    hoverStyle=arrow_function(
                        dict(weight=4, fillOpacity=0.2, dashArray="")
                    ),
					id="zips-geojson")
    zip_overlay = dl.Overlay(zips, name="zips", checked=True)
    return zip_overlay

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


