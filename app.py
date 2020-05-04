import os

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from wordcloud import WordCloud

import pandas as pd
import plotly.express as px

from places import places
from characters import characters

import random

import numpy as np
from dash.exceptions import PreventUpdate

df = pd.read_csv("pulp_fiction_dialogue.csv")

def characters_checkboxes():
	result = []
	for character in df.Character.unique():
		result.append({'label': character, 'value': character})
	return result

def places_checkboxes():
	result = []
	for place in df.Place.unique():
		result.append({'label': place, 'value': place})
	return result

def times_checkboxes():
	result = []
	for time in df.Time.unique():
		result.append({'label': time, 'value': time})
	return result

def random_line(df):
	if len(df) == 0:
		return "You have filtered out all data!"
	line = df.iloc[random.randrange(len(df))]
	return f"Line {line.iloc[0]}, {line.Character}: \"{line.Line}\""

def word_cloud(df):
	words = ""
	for line in df["Line"]:
		words = " ".join([words, line])
	if len(df) == 0:
		words = "Empty"
	wordcloud = WordCloud(background_color='white', width=800, height=280).generate(words)
	img = wordcloud.to_image()
	fig = px.imshow(img, width=img.width, height=img.height)
	fig.update_xaxes(showticklabels=False)
	fig.update_yaxes(showticklabels=False)
	fig.update_layout({"hovermode":False, "margin":{"l":0, "r":0, "t":0, "b":0, }})
	return fig

def word_count(df):
	words = df.groupby("Character").sum().sort_values("Word count", ascending = False)
	#return px.bar(words, x=words.index, y=words["Word count"])
	return px.bar(df, x="Character", y="Word count", color="Word count", hover_data=df.columns, color_continuous_scale=px.colors.sequential.Blugrn)

def filtered_dataframe(f_characters, f_places, f_times):
	filtered = df.copy()
	filtered = filtered[filtered.Character.isin(f_characters)]
	filtered = filtered[filtered.Place.isin(f_places)]
	filtered = filtered[filtered.Time.isin(f_times)]
	return filtered


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div([
    html.H1('Pulp Fiction'),

	html.Div(children='''
        Exploratory interactive visualization of the dialogue of the movie Pulp Fiction
    '''),

	html.Div([
		html.H4('Characters'),
		html.Div(
		dcc.Checklist(
			id='filter-characters',
    		options=characters_checkboxes(),
			value=df.Character.unique()
		),
		style={"overflow": "auto",
			   "height":"200px",
			   "width": "200px"}
		),
		html.Button('All', id='btn-all-characters', title="Select all characters"),
		html.Button('Clear', id='btn-clear-characters', title="Unselect all characters")
		],
		style={"display": "inline-block", "margin": "1em"}
	),

	html.Div([
		html.H4('Locations'),
		html.Div(
			dcc.Checklist(
				id='filter-places',
				options=places_checkboxes(),
				value=df.Place.unique()
			),
			style={"overflow": "auto",
				"height":"200px",
				"width": "200px"}
		),
		html.Button('All', id='btn-all-places', title="Select all locations"),
		html.Button('Clear', id='btn-clear-places', title="Unselect all locations"),
		],
		style={"display": "inline-block", "margin": "1em"}
	),

	html.Div([
		html.H4('Time of day'),
		html.Div(
			dcc.Checklist(
				id='filter-times',
				options=times_checkboxes(),
				value=df.Time.unique()
			),
			style={"overflow": "auto",
				"height":"200px",
				"width": "200px"}
		),
		html.Button('All', id='btn-all-times', title="Select all times of day"),
		html.Button('Clear', id='btn-clear-times', title="Unselect all times of day"),
		],
		style={"display": "inline-block", "margin": "1em"}
	),

	html.Div(
		dcc.Graph(
			id='word-cloud',
			figure=word_cloud(df),
			config={'staticPlot': True}
		),
		style={"display": "inline-block"}
	),

	html.Div(
		children=random_line(df),
		id='random-line',
		style={
			'text-align': 'right'
		}
	),

	dcc.Graph(
			id='word-count',
			figure=word_count(df)
	),

	html.Div(
		id='clicked-line'
	),
])

@app.callback(
	Output(component_id='filter-characters', component_property='value'),
	[Input(component_id='btn-clear-characters', component_property='n_clicks'),
	 Input(component_id='btn-all-characters', component_property='n_clicks')]
)
def select_or_clear_all_characters(clear_btn, all_btn):
	if clear_btn is None and all_btn is None:
		raise PreventUpdate
	changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
	if 'btn-all-characters' in changed_id:
		return df.Character.unique()
	elif 'btn-clear-characters' in changed_id:
		return []

@app.callback(
	Output(component_id='filter-places', component_property='value'),
	[Input(component_id='btn-clear-places', component_property='n_clicks'),
	 Input(component_id='btn-all-places', component_property='n_clicks')]
)
def select_or_clear_all_places(clear_btn, all_btn):
	if clear_btn is None and all_btn is None:
		raise PreventUpdate
	changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
	if 'btn-all-places' in changed_id:
		return df.Place.unique()
	elif 'btn-clear-places' in changed_id:
		return []

@app.callback(
	Output(component_id='filter-times', component_property='value'),
	[Input(component_id='btn-clear-times', component_property='n_clicks'),
	 Input(component_id='btn-all-times', component_property='n_clicks')]
)
def select_or_clear_all_times(clear_btn, all_btn):
	if clear_btn is None and all_btn is None:
		raise PreventUpdate
	changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
	if 'btn-all-times' in changed_id:
		return df.Time.unique()
	elif 'btn-clear-times' in changed_id:
		return []

@app.callback(
    Output('clicked-line', 'children'),
    [Input('word-count', 'clickData')])
def display_click_data(clickData):
	if clickData is None:
		return "Click a line in the bar chart to see more detailed information here!"

	#line_info = clickData['points'][0]['customdata']
	print(clickData)
	line_number = clickData['points'][0]['customdata'][0]
	line_info = df.iloc[line_number-1]
	d = {'Line number': line_info[0],
  		'Character': line_info[1],
  		'Off screen': line_info[2],
  		'Place': line_info[3],
  		'Time': line_info[4],
		'Word count': line_info[6],
  		'Line': line_info[5]}

	result=[]
	for k, v in d.items():
		s = ": ".join((str(k),str(v)))
		result.append(html.P(s))

	return result

@app.callback(
	[Output(component_id='word-count', component_property='figure'),
	 Output(component_id='random-line', component_property='children'),
	 Output(component_id='word-cloud', component_property='figure')],
	[Input(component_id='filter-characters', component_property='value'),
	 Input(component_id='filter-places', component_property='value'),
	 Input(component_id='filter-times', component_property='value')]
)
def filter_graphs(f_characters, f_places, f_times):
	if f_characters is None or f_places is None or f_times is None:
		f_characters = f_places = f_times = []
	f = filtered_dataframe(f_characters, f_places, f_times)
	return word_count(f), random_line(f), word_cloud(f)

if __name__ == '__main__':
    app.run_server(debug=True)