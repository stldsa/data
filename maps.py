import os
import requests
from pathlib import Path
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
    geo_df.to_file(output_path, driver="GeoJSON")
