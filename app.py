import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_leaflet as dl
import plotly.express as px
import pandas as pd

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_csv("data/all_donations.csv")

app.layout = dl.Map(dl.TileLayer(), style={"width": "1000px", "height": "500px"})

if __name__ == "__main__":
    app.run_server(debug=True)