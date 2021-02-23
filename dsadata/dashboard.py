import dash
import dash_html_components as html
import dash_bootstrap_components as dbc
import locale
from dotenv import load_dotenv
from flask.cli import with_appcontext
from dsadata.bootstrap_stuff import get_sidebar_layout

load_dotenv()
from dash.dependencies import Output, Input, State

# from dsadata.mec_query import db
from dsadata import init_app, bootstrap_stuff

locale.setlocale(locale.LC_ALL, "en_US.UTF-8")

# server = init_app()
# server.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
# server.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# db.init_app(server)


# from mec_query import Candidate


def init_dashboard(server):
    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix="/",
        external_stylesheets=[dbc.themes.BOOTSTRAP],
    )
    dash_app.layout = get_sidebar_layout()
    # dash_app.layout = html.Div(id="dash-container")
    init_callbacks(dash_app)
    return dash_app.server


def init_callbacks(app):
    # pass
    @app.callback(
        [Output("zips-geojson", "hideout")],
        [Input("fundraising-graph", "hoverData")],
    )
    def display_choropleth(hovered_data):
        if hovered_data is not None:
            candidate_row = (
                db.session.query(Candidate)
                .filter_by(name=hovered_data["points"][0]["label"])
                .first()
            )
            mec_id = candidate_row.mec_id
            color_prop = "mec_donazzzzzzzzzzzzzzzzzztion_" + mec_id
        else:
            color_prop = "total_mayor_donations"
        hideout = bootstrap_stuff.build_choropleth_hideout(color_prop)
        return [hideout]

    # Candidate Selected: Look at stats from that candidate
    @app.callback(
        [
            Output("candidate_info_collapse", "is_open"),
            Output("candidate_info_collapse", "children"),
            Output("precincts-geojson", "hideout"),
            Output("neighborhood-geojson", "hideout"),
            Output("zip-geojson", "hideout"),
        ],
        [Input("fundraising-graph", "clickData")],
        [State("candidate_info_collapse", "is_open")],
    )
    def toggle_collapse(clicked_data, is_open):
        if clicked_data:
            candidate_row = (
                db.session.query(Candidate)
                .filter_by(name=clicked_data["points"][0]["label"])
                .first()
            )
            mec_id = candidate_row.mec_id
            color_prop = "mec_donations_" + mec_id
            hideout = bootstrap_stuff.build_choropleth_hideout(color_prop)
            return (
                True,
                [bootstrap_stuff.get_candidate_info_card(candidate_row)],
                hideout,
                hideout,
                hideout,
            )
        hideout = bootstrap_stuff.build_choropleth_hideout("total_monetary_donations")
        return (
            False, 
            [], 
            hideout, 
            hideout, 
            hideout
        )

    # @app.callback(
    #     Output("base-layer-name", "children"),
    #     [Input("geojson-layer-control", "baseLayer")],
    # )
    # def layer_change(base_layer):
    #     # TODO: We need to probably add an indication of how much $ we aren't showing, either b/c address etc is missing, or it is out of view (e.g. not in a STL city neighborhood/precinct)
    #     return base_layer

    @app.callback(
        [
            Output("precinct-baselayer", "checked"),
            Output("neighborhood-baselayer", "checked"),
            Output("zip-baselayer", "checked"),
            Output("precinct-button", "active"),
            Output("neighborhood-button", "active"),
            Output("zip-button", "active"),
        ],
        [
            Input("precinct-button", "n_clicks"),
            Input("neighborhood-button", "n_clicks"),
            Input("zip-button", "n_clicks"),
        ],
    )
    def layer_button_click(precinct_clicks, neighborhood_clicks, zip_clicks):
        changed_id = [p["prop_id"] for p in dash.callback_context.triggered][0]
        if "precinct-button" in changed_id:
            return [True, False, False, True, False, False]
        elif "neighborhood-button" in changed_id:
            return [False, True, False, False, True, False]
        elif "zip-button" in changed_id:
            return [False, False, True, False, False, True]
        else:
            return [True, False, False, True, False, False]

    @app.callback(
        [
            Output("floatbox-neighborhood", "children"),
            Output("floatbox-neighborhood", "className"),
        ],
        [
            Input("neighborhood-geojson", "click_feature"),
            Input("card-box-close-neighborhood", "n_clicks"),
        ],
    )
    def neighborhood_click(feature, n_clicks):
        class_name = "displayNone"
        header_text = "Error"
        card_contents = bootstrap_stuff.get_floatbox_card_contents("neighborhood")

        if feature:
            if (
                "NHD_NAME" in feature["properties"]
                and feature["properties"]["NHD_NAME"]
            ):
                header_text = feature["properties"]["NHD_NAME"]
            else:
                header_text = feature["properties"]["MUNICIPALI"].title()
            body_contents = [
                html.Strong("Total monetary donations: "),
                html.Span(
                    locale.currency(
                        feature["properties"]["total_monetary_donations"], grouping=True
                    )
                ),
            ]
            class_name = "floatbox"
            card_contents = bootstrap_stuff.get_floatbox_card_contents(
                "neighborhood", header_text, body_contents
            )

        if n_clicks:
            class_name = "displayNone"

        return [card_contents, class_name]

    @app.callback(
        [
            Output("floatbox-precinct", "children"),
            Output("floatbox-precinct", "className"),
        ],
        [
            Input("precincts-geojson", "click_feature"),
            Input("card-box-close-precinct", "n_clicks"),
        ],
    )
    def precinct_click(feature, n_clicks):
        class_name = "displayNone"
        header_text = "Error"
        card_contents = bootstrap_stuff.get_floatbox_card_contents("precinct")

        if feature:
            print(feature["properties"])
            if (
                "WARD10" in feature["properties"] and feature["properties"]["WARD10"]
            ):  # STL City precinct
                header_text = f"STL City: Ward {feature['properties']['WARD10']}, Precinct {feature['properties']['PREC10']}"
            elif feature["properties"]["PRECINCTID"]:  # STL County precinct
                header_text = (
                    f"STL County: Precinct {feature['properties']['PRECINCTID']}"
                )
            body_contents = [
                html.Strong("Total monetary donations: "),
                html.Span(
                    locale.currency(
                        feature["properties"]["total_monetary_donations"], grouping=True
                    )
                ),
            ]
            class_name = "floatbox"
            card_contents = bootstrap_stuff.get_floatbox_card_contents(
                "precinct", header_text, body_contents
            )

        if n_clicks:
            class_name = "displayNone"

        return [card_contents, class_name]

    @app.callback(
        [Output("floatbox-zip", "children"), Output("floatbox-zip", "className")],
        [
            Input("zip-geojson", "click_feature"),
            Input("card-box-close-zip", "n_clicks"),
        ],
    )
    def zip_click(feature, n_clicks):
        class_name = "displayNone"
        header_text = "Error"
        card_contents = bootstrap_stuff.get_floatbox_card_contents("zip")

        if feature:
            header_text = f"ZIP Code {feature['properties']['ZCTA5CE10']}"
            body_contents = [
                html.Strong("Total monetary donations: "),
                html.Span(
                    locale.currency(
                        feature["properties"]["total_monetary_donations"], grouping=True
                    )
                ),
            ]
            class_name = "floatbox"
            card_contents = bootstrap_stuff.get_floatbox_card_contents(
                "zip", header_text, body_contents
            )

        if n_clicks:
            class_name = "displayNone"

        return [card_contents, class_name]
