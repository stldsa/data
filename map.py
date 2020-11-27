import dash
import dash_html_components as html
import dash_leaflet as dl
import dash_leaflet.express as dlx
import pandas as pd
import json

from dash.dependencies import Output, Input

keys = ["watercolor", "toner", "terrain"]
url_template = "http://{{s}}.tile.stamen.com/{}/{{z}}/{{x}}/{{y}}.png"
attribution = 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, ' \
              '<a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data ' \
              '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'

df = pd.read_csv("data/elections/2020-general-election.csv")

with open("data/geojson/stl-city/wards.json") as read_file:
	ward_geojson = json.load(read_file)
	for ward_object in ward_geojson["features"]:
		df_ward = df[df["Ward"] == ward_object["properties"]["Ward"]]
		ward_object["properties"]["Turnout"] = df_ward.iloc[0]["Turnout"]

color_prop = 'Turnout'

def get_info(feature=None):
	header = [html.H4("Ward Turnout")]
	if not feature:
		return header + ["Hover over a ward"]
	
	return header + [html.B(str(feature["properties"]["Ward"])+"th ward"), html.Br(),
						"Turnout: {:.2f}%".format(feature["properties"]["Turnout"])
						]

classes = [30, 40, 50, 60, 70, 80]
colorscale = ['#FEB24C', '#FD8D3C', '#FC4E2A', '#E31A1C', '#BD0026', '#800026']
style = dict(weight=2, opacity=1, color='white', dashArray='3', fillOpacity=0.7)

# Colorbar
ctg = ["{}%+".format(cls, classes[i + 1]) for i, cls in enumerate(classes[:-1])] + ["{}%+".format(classes[-1])]
colorbar = dlx.categorical_colorbar(categories=ctg, colorscale=colorscale, width=300, height=30, position="bottomright")

# Create geojson.
wards = dl.GeoJSON(data=ward_geojson,  # data, not url to geojson file (why wasn't url working?)
                     options=dict(style=dlx.choropleth.style),  # how to style each polygon
                     zoomToBounds=True,  # when true, zooms to bounds when data changes (e.g. on load)
                     zoomToBoundsOnClick=True,  # when true, zooms to bounds of feature (e.g. polygon) on click
                     hoverStyle=dict(weight=5, color='#fff', dashArray=''),  # special style applied on hover
                     hideout=dict(colorscale=colorscale, classes=classes, style=style, color_prop="Turnout"),
                     id="wards")

# Create info control
info = html.Div(id="info", className="info",
				style={"position": "absolute", "top": "10px", "right": "80px", "zIndex": "1000"})

# Create app
app = dash.Dash(prevent_initial_callbacks=True)
app.layout = html.Div([
	dl.Map([
		dl.LayersControl(
			[dl.BaseLayer(dl.TileLayer(url=url_template.format(key), attribution=attribution),
				name=key, checked=key == "toner") for key in keys] +
			[dl.Overlay(dl.LayerGroup(wards), name="wards", checked=True)]
		),
		colorbar
	], zoom=11, center=[38.681, -90.313], style={"width": "100%", "height": "100vh", "margin": "none", "display": "block"}, 
	id="map"),
	info
])

@app.callback(Output("info", "children"), Input("wards", "hover_feature"))

def info_hover(feature):
	return get_info(feature)

	
if __name__ == "__main__":
  app.run_server(debug=True)