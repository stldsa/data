# import pytest
# import shapefile
# import shutil
# import pandas as pd
# import geopandas as gp
# import datatest as dt
# from pathlib import Path

# from dsadata import maps


# @pytest.fixture(scope="module")
# def shapefile_dir(tmp_path_factory):
#     shapefile_dir = tmp_path_factory.mktemp(basename="test_dir", numbered=False)
#     shapefile_path = Path(shapefile_dir / "testfile")
#     with shapefile.Writer(shapefile_path) as w:
#         w.field("field1", "C")
#         w.shapetype = 3
#         w.field("TEXT", "C")
#         w.field("SHORT_TEXT", "C", size=5)
#         w.field("LONG_TEXT", "C", size=250)
#         w.null()
#         w.record("Hello", "World", "World" * 50)
#     return shapefile_dir


# @pytest.fixture(scope="module")
# def zip_path(shapefile_dir):
#     zip_path = Path(shutil.make_archive(shapefile_dir, "zip", shapefile_dir))
#     return zip_path


# @pytest.fixture(scope="module")
# def results_df():
#     results = pd.read_csv("data/elections/results.csv")
#     return results


# @pytest.fixture(scope="module")
# def contests_df():
#     contests = pd.read_csv(
#         "data/elections/contests.csv", index_col=["Election Date", "Ballot Item"]
#     )
#     return contests


# def test_download_shp_zip(requests_mock, tmp_path):
#     requests_mock.get("https://www.test-url.com/test_file.zip")
#     filepath = tmp_path / "test_file.zip"

#     maps.download_shp_zip(
#         "https://www.test-url.com/test_file.zip",
#         output_dir=tmp_path,
#     )
#     assert filepath.exists()


# def test_convert_file_to_geojson(zip_path):
#     specifier = Path("testfile.shp")
#     output_path = zip_path.parent / specifier.with_suffix(".json")

#     maps.convert_to_geojson(zip_path, specifier)

#     assert output_path.exists()
#     assert ".shp" not in output_path.name
#     df = gp.read_file(output_path)
#     dt.validate.subset(df.columns, {"field1", "TEXT", "geometry"})


# # def test_ward_contest_results_figures(contests_df):
# #     results_figures = maps.results_figures(contests_df)
# #     assert len(results_figures.data) == len(contests_df)


# # def test_ward_click()