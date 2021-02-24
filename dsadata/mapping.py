import json

import geopandas as gpd

import dash_leaflet as dl
import dash_leaflet.express as dlx
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash_extensions.javascript import arrow_function, Namespace
import dash_daq as daq

from dsadata import plotting, bootstrap_stuff, contrib

import plotly.express as px


def get_expand_button():
    expand_button = daq.ToggleSwitch(size=50, id="expand-side-swith")
    return expand_button


def get_candidate_select(candidates):
    selection = dcc.RadioItems(
        id="candidate-select",
        options=[{"value": c.mec_id, "label": c.name} for c in candidates],
        value=candidates[0].mec_id,
        labelStyle={"display": "inline-block"},
        className="candidateSelect",
    )
    return selection


def reset_selection_button():
    reset_button = html.Button("Reset", id="reset-candidate-button")
    return reset_button


def get_colorbar():
    colorbar = dlx.categorical_colorbar(
        id="colorbar",
        categories=bootstrap_stuff.fundraising_ctg,
        colorscale=bootstrap_stuff.fundraising_colorscale,
        width=400,
        height=30,
        position="topright"
    )
    return colorbar


def get_zip_geojson():
    ns = Namespace("dlx", "choropleth")
    zip_geobuf_path = "static/geobuf/stl-region-zip.pbf"
    zip_geojson = dl.GeoJSON(
        url=zip_geobuf_path,
        format="geobuf",
        options=dict(style=ns("style")),  # how to style each polygon
        # options=dict(style=dict(color="blue")),
        zoomToBounds=False,  # when true, zooms to bounds when data changes (e.g. on load)
        zoomToBoundsOnClick=False,  # when true, zooms to bounds of feature (e.g. polygon) on click
        hoverStyle=arrow_function(dict(weight=5, color="#666", dashArray="")),
        hideout=bootstrap_stuff.build_choropleth_hideout("total_monetary_donations"),
        id="zip-geojson",
    )
    return zip_geojson


def get_precinct_geojson():
    ns = Namespace("dlx", "choropleth")
    precincts_geobuf_path = "static/geobuf/stl-city-and-county-precincts.pbf"
    precincts_geojson = dl.GeoJSON(
        url=precincts_geobuf_path,
        format="geobuf",
        options=dict(style=ns("style")),
        hoverStyle=arrow_function(dict(weight=5, color="#666", dashArray="")),
        hideout=bootstrap_stuff.build_choropleth_hideout("total_monetary_donations"),
        id="precincts-geojson",
    )
    return precincts_geojson


def get_neighborhood_geojson():
    ns = Namespace("dlx", "choropleth")
    neighborhoods_geobuf_path = "static/geobuf/neighborhoods-and-municipalities.pbf"
    neighborhoods_geojson = dl.GeoJSON(
        url=neighborhoods_geobuf_path,
        format="geobuf",
        options=dict(style=ns("style")),
        hoverStyle=arrow_function(dict(weight=5, color="#666", dashArray="")),
        hideout=bootstrap_stuff.build_choropleth_hideout("total_monetary_donations"),
        id="neighborhood-geojson",
    )
    return neighborhoods_geojson


def get_map_panel_layout():
    colorbar = get_colorbar()
    stl_center = [38.648, -90.253]
    city_map_style = {"height": "100%", "margin": "none", "display": "block"}
    city_map = html.Div(
        dl.Map(
            children=[
                get_base_toner_tile_layer(),
                dl.LayersControl(
                    children=[
                        dl.BaseLayer(
                            get_precinct_geojson(),
                            name="precinct",
                            id="precinct-baselayer",
                            checked=True,
                        ),
                        dl.BaseLayer(
                            get_neighborhood_geojson(),
                            name="neighborhood",
                            id="neighborhood-baselayer",
                        ),
                        dl.BaseLayer(get_zip_geojson(), name="zip", id="zip-baselayer"),
                    ],
                    id="geojson-layer-control",
                ),
                colorbar,
            ],
            zoom=12,
            center=stl_center,
            id="city-map",
        ),
        style=city_map_style,
        id="map",
    )

    precinct_card = dbc.Card(
        children=bootstrap_stuff.get_floatbox_card_contents("precinct"),
        color="dark",
        outline=True,
        id="floatbox-precinct",
        className="displayNone",
    )
    neighborhood_card = dbc.Card(
        children=bootstrap_stuff.get_floatbox_card_contents("neighborhood"),
        color="dark",
        outline=True,
        id="floatbox-neighborhood",
        className="displayNone",
    )
    zip_card = dbc.Card(
        children=bootstrap_stuff.get_floatbox_card_contents("zip"),
        color="dark",
        outline=True,
        id="floatbox-zip",
        className="displayNone",
    )

    map_panel_style = {"width": "100%", "display": "block"}
    map_panel = html.Div(
        id="map-panel",
        children=[
            city_map,
            html.Div(
                children=[precinct_card, neighborhood_card, zip_card],
                id="floatbox-holder",
            ),
        ],
        style=map_panel_style,
    )
    return map_panel


def get_precinct_overlay():
    # original file was wrong hand rule, whis one was rewound with geojson-rewind:
    precinct_pbf_url = "static/geobuf/stl-city-precincts.pbf"
    ns = Namespace("dlx", "choropleth")
    precincts = dl.GeoJSON(
        url=precinct_pbf_url,
        format="geobuf",
        options=dict(style=ns("style")),
        zoomToBoundsOnClick=True,
        hoverStyle=arrow_function(dict(weight=4, fillOpacity=0.2, dashArray="")),
        hideout=bootstrap_stuff.build_choropleth_hideout("total_donations"),
        id="precincts-geojson",
    )
    precinct_overlay = dl.Overlay(precincts, name="precincts", checked=False)
    return precinct_overlay


def get_base_toner_tile_layer():
    # 	Base tile layer
    url = "http://{s}.tile.stamen.com/toner/{z}/{x}/{y}.png"
    attribution = (
        'Map tiles by <a href="http://stamen.com">Stamen Design</a>, '
        'under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. '
        'Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.'
    )
    base_tile_layer = dl.TileLayer(url=url, attribution=attribution)
    return base_tile_layer
