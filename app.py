import json

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import State, Output, Input

import pandas as pd
import dash_leaflet as dl


app = dash.Dash(
	__name__,
	meta_tags=[
		{"name":"viewport", "content":"width=device-width, initial-scale=1.0"}
	],
)

#	You should be able to use any path to a CSV with a "Ward" column, just modify the process_row function as necessary
election_data_by_ward_path = "data/elections/2020-general-election.csv"
def process_election_data_row(row):
	cells = row.split(',')
	return dict(
		ward=cells[0],
		stats=dict(
			reg_voters=int(cells[1]),
			ballots_cast=int(cells[2])
		),
		president=dict(
			trump=int(cells[3]),
			biden=int(cells[4])
		),
		prop_d=dict(
			yes=int(cells[5]),
			no=int(cells[6])
		),
		prop_1=dict(
			yes=int(cells[7]),
			no=int(cells[8])
		),
		prop_r=dict(
			yes=int(cells[9]),
			no=int(cells[10])
		)
	)	
with open(election_data_by_ward_path, 'r') as f:
	results_by_ward = {}
	next(f)	# skip the first line
	ward_num = 1
	for line in f:
		results_by_ward[str(int(ward_num))] = process_election_data_row(line)
		ward_num = ward_num + 1

# SIDE PANEL
# Set up side panel: used to choose stuff and display data
side_panel_text = "Donor project"
side_panel_layout = html.Div(
	id='panel-side',
	children=[
		side_panel_text
	],
	style={"width": "30%", "max-width":"450px", "color": "white", "background-color": "red"}
)

# MAP PANEL
#	Base tile layer
url = "http://{s}.tile.stamen.com/toner-background/{z}/{x}/{y}.png"
attribution = 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, ' \
			'under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. ' \
			'Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.'
base_tile_layer = dl.TileLayer(url=url, attribution=attribution)


#	Ward overlay
df = pd.read_csv(election_data_by_ward_path)
ward_geojson_path = "data/geojson/stl-city/wards.json"
with open(ward_geojson_path) as read_file:
	ward_geojson = json.load(read_file)
	for ward_object in ward_geojson["features"]:
		df_ward = df[df["Ward"] == ward_object["properties"]["Ward"]]
		ward_object["properties"]["extra_data"] = results_by_ward[str(int(ward_object["properties"]["Ward"]))]

wards = dl.GeoJSON(data=ward_geojson,
					zoomToBoundsOnClick=True,  # when true, zooms to bounds of feature (e.g. polygon) on click
					hoverStyle=dict(weight=5, color='#fff', dashArray=''),  # special style applied on hover)
					id="wards-geojson")
ward_overlay = dl.Overlay(dl.LayerGroup(wards), name="wards", checked=True)

#	Map and wrapper
city_map = html.Div(
	children=[
		dl.Map(dl.LayersControl([base_tile_layer, ward_overlay]),
			zoom=11, center=[38.681, -90.313], 
			style={"width": "100%", "height": "100vh", "margin": "none", "display": "block"}
		)
	],
	id='city-map-wrapper',
)

map_panel_layout = html.Div(
	id='map-panel',
	children=[
		city_map,
		"hello"
	], 
	style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"}
)

# ROOT
root_layout = html.Div(
	id='root',
	children=[
		side_panel_layout,
		map_panel_layout
	],
	style={"display": "flex", "flex-direction": "row-reverse", "margin": 0}
)

app.layout = root_layout

if __name__ == "__main__":
	app.run_server(debug=True)

