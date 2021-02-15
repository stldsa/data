import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd

import mapping
from mec_query import Candidate, Contributor, Contribution

import locale
locale.setlocale( locale.LC_ALL, '' )

def get_error_404(pathname):
	return dbc.Jumbotron(
		[
			html.H1("404: Not found", className="text-danger"),
			html.Hr(),
			html.P(f"The pathname {pathname} was not recognized")
		]
	)

def get_sidebar_layout(db):
	candidates = Candidate.query.all()
	mec_ids = ["C201499", "C201099", "C201500", "C211544"]
	mec_df = pd.read_sql(db.session.query(Contribution).statement, db.session.bind)
	return dbc.Container([
		dbc.Row([
			dbc.Col(
				mapping.get_side_panel_layout(candidates, mec_df),
				width=4
			),
			dbc.Col(
				mapping.get_map_panel_zip_layout(), 
				width=8
			)
		], 
		no_gutters=True)
	], fluid=True, className="remove-padding")

def show_zip_click_card(feature):
	header_style = {"fontSize":"1.5em", "fontWeight":"bold"}
	card_content = [
		dbc.CardHeader(
			[
				html.Span(f"ZIP Code {feature['properties']['ZCTA5CE10']}", style=header_style),
				# dbc.Button(" X ", outline=True, color="danger", id="zip-box-close", style={"float":"right"})
			]),
		dbc.CardBody(
			[
            	html.Strong("Total funds contributed for Mayor's race: "),
				html.Span(locale.currency( feature['properties']['total_mayor_donations'], grouping=True))
			]
		)
	]
	zip_card = dbc.Card(card_content, color="dark", outline=True, id="floatbox")
	return zip_card

