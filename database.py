import geopandas as gp
from sqlalchemy import create_engine
zip_geojson = gp.read_file('data/geojson/stl-region-zip_rw.geojson')
connection_url="postgresql://meagles:password@localhost:5432/dsadata"
engine = create_engine(connection_url)
zip_geojson.to_postgis(name="zip_geojson", con=engine)