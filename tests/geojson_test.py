# import os, json
# import dash
# import dash_html_components as html
# import dash_bootstrap_components as dbc
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from dotenv import load_dotenv
# import plotly.express as px
# import dash_leaflet as dl
# import dash_leaflet.express as dlx
# from dash_extensions.javascript import arrow_function, Namespace
# import pandas as pd
# from dsadata import mapping, contrib, plotting
# from dsadata.mec_query import Candidate, Contribution, Contributor

# candidates = Candidate.query.all()

# mec_id = None
# contribution_df = pd.read_sql(db.session.query(Contribution).statement, db.session.bind)
# contributor_df = pd.read_sql(db.session.query(Contributor).statement, db.session.bind)
# mec_df = contribution_df.merge(
#     contributor_df, left_on="contributor_id", right_index=True
# )

# geojson_data = contrib.build_zip_amount_geojson(mec_df)

# classes = [0, 100, 500, 1000, 2000, 5000, 10000, 20000]
# colorscale = [
#     "#FFEDA0",
#     "#FED976",
#     "#FEB24C",
#     "#FD8D3C",
#     "#FC4E2A",
#     "#E31A1C",
#     "#BD0026",
#     "#800026",
# ]
# style = {
#     "weight": 2,
#     "opacity": 1,
#     "color": "white",
#     "dashArray": 3,
#     "fillOpacity": 0.7,
# }

# ctg = ["{}+".format(cls, classes[i + 1]) for i, cls in enumerate(classes[:-1])] + [
#     "{}+".format(classes[-1])
# ]
# colorbar = dlx.categorical_colorbar(
#     categories=ctg, colorscale=colorscale, width=400, height=30, position="bottomright"
# )

# ns = Namespace("dlx", "choropleth")
# zip_geojson = dl.GeoJSON(
#     data=geojson_data,  # url to geojson file
#     options=dict(style=ns("style")),  # how to style each polygon
#     zoomToBounds=False,  # when true, zooms to bounds when data changes (e.g. on load)
#     zoomToBoundsOnClick=True,  # when true, zooms to bounds of feature (e.g. polygon) on click
#     hoverStyle=arrow_function(
#         dict(weight=5, color="#666", dashArray="")
#     ),  # style applied on hover
#     hideout=dict(
#         colorscale=colorscale, classes=classes, style=style, colorProp="Amount"
#     ),
#     id="zips-geojson",
# )

# stl_center = [38.648, -90.253]
# city_map_style = {"height": "100vh", "margin": "none", "display": "block"}
# city_map = html.Div(
#     dl.Map(
#         children=[mapping.get_base_toner_tile_layer(), zip_geojson, colorbar],
#         zoom=12,
#         center=stl_center,
#     ),
#     style=city_map_style,
#     id="map",
# )

# map_panel_style = {"width": "100%", "height": "100vh", "display": "block"}
# map_panel = html.Div(id="map-panel", children=city_map, style=map_panel_style)

# root_layout = html.Div(
#     id="root",
#     children=[map_panel],
#     style={"display": "flex", "flexDirection": "row", "margin": 0},
# )

# app.layout = root_layout

# if __name__ == "__main__":
#     app.run_server(debug=True)