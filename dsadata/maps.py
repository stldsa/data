import requests
from pathlib import Path
import plotly.express as px
import pandas as pd
import geopandas as gp


def download_shp_zip(url, output_dir=Path("data/geodata/"), chunk_size=128):
    r = requests.get(url, stream=True)
    filename = Path(url).name
    with open(output_dir / filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=chunk_size):
            f.write(chunk)


def convert_to_geojson(filepath, specifier=""):
    filepath = Path(filepath)
    if filepath.suffix == ".zip":
        shapefile_dir = filepath.parent
        if specifier:
            shapefile_path = "zip://" + str(filepath) + "!" + str(specifier)
            output_path = Path(shapefile_dir / specifier).with_suffix(".json")
    geo_df = gp.read_file(shapefile_path)
    if not geo_df.crs:
        geo_df.crs = "epsg:4326"
    geo_df = geo_df.to_crs("EPSG:4326")
    geo_df.to_file(output_path, driver="GeoJSON")


def results_figures(contests_df):
    results_df = pd.read_csv(
        "data/elections/results.csv",
        index_col=["Election Date", "Ward", "Ballot Item", "Ballot Selection"],
    )
    contests_results = contests_df.join(results_df)
    results_figs = px.bar(
        contests_results.reset_index(),
        x="Ballot Item",
        y="votes",
        facet_col="Name",
    )
    return results_figs
