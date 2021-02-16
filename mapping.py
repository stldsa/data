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
import bootstrap_stuff

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


def get_map_panel_zip_layout():
    colorbar = dlx.categorical_colorbar(
        id="colorbar",
        categories=bootstrap_stuff.fundraising_ctg,
        colorscale=bootstrap_stuff.fundraising_colorscale,
        width=400,
        height=30,
        position="bottomright",
    )

    ns = Namespace("dlx", "choropleth")
    zip_geojson = dl.GeoJSON(
        url="/static/geobuf/stl-region-zip.pbf", format="geobuf",
        options=dict(style=ns("style")),  # how to style each polygon
        # options=dict(style=dict(color="blue")),
        zoomToBounds=False,  # when true, zooms to bounds when data changes (e.g. on load)
        zoomToBoundsOnClick=False,  # when true, zooms to bounds of feature (e.g. polygon) on click
        hoverStyle=arrow_function(
            dict(weight=5, color="#666", dashArray="")
        ),  # style applied on hover
        hideout=bootstrap_stuff.build_choropleth_hideout("total_mayoral_donations"),
        id="zips-geojson",
    )

    stl_center = [38.648, -90.253]
    city_map_style = {"height": "100vh", "margin": "none", "display": "block"}
    city_map = html.Div(
        dl.Map(
            children=[get_base_toner_tile_layer(), zip_geojson, colorbar],
            zoom=12,
            center=stl_center,
        ),
        style=city_map_style,
        id="map",
    )
    map_panel_style = {"width": "100%", "height": "100vh", "display": "block"}
    map_panel = html.Div(id="map-panel", 
        children=[
            city_map, 
            html.Div(children=[bootstrap_stuff.get_zip_click_card(None)], id="floatbox-holder")
        ], 
        style=map_panel_style)
    return map_panel


def get_precinct_overlay():
    # original file was wrong hand rule, whis one was rewound with geojson-rewind:
    precinct_geojson_path = "data/geojson/stl-city/precincts_rw.geojson"
    with open(precinct_geojson_path) as read_file:
        precinct_geojson = json.load(read_file)
    precincts = dl.GeoJSON(
        data=precinct_geojson,
        options=dict(style=dict(color="blue", fillOpacity=0.5)),
        zoomToBoundsOnClick=True,
        hoverStyle=arrow_function(dict(weight=4, fillOpacity=0.2, dashArray="")),
        id="precincts-geojson",
    )
    precinct_overlay = dl.Overlay(precincts, name="precincts", checked=False)
    return precinct_overlay


def get_zip_overlay(mec_df, candidate):
    if candidate is not None:
        cand_df = contrib.sum_funds_by_zip(cand_zip_df)
    else:
        df = cand_zip_df[cand_zip_df[" MECID"] == candidate]
    # original file was wrong hand rule, whis one was rewound with geojson-rewind:
    zip_geojson_path = "data/geojson/stl-region-zip_rw.geojson"
    gdf = gpd.read_file(zip_geojson_path)
    gdf = gdf.merge(cand_zip_df, left_on="ZCTA5CE10", right_on="ZIP5")
    if candidate is not None:
        df = contrib.sum_funds_by_zip(cand_zip_df)
    else:
        df = cand_zip_df[cand_zip_df[" MECID"] == candidate]
    with open(zip_geojson_path) as read_file:
        zip_geojson = json.load(read_file)
    zips = dl.GeoJSON(
        data=zip_geojson,
        options=dict(style=dict(color="purple", fillOpacity=0.5)),
        zoomToBoundsOnClick=True,
        hoverStyle=arrow_function(dict(weight=4, fillOpacity=0.2, dashArray="")),
        id="zips-geojson",
    )
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
