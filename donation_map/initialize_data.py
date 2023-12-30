import maps

maps.download_shp_zip(
    "https://www.stlouis-mo.gov/data/upload/data-files/nbrhds_wards.zip"
)

maps.convert_to_geojson("data/geodata/nbrhds_wards.zip", "WARDS_2010.shp")
