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

df = pd.read_csv("pulp_fiction_dialogue.csv")

def characters_checkboxes():
	result = []
	for character in characters:
		result.append({'label': character.title(), 'value': character.title()})
	return result

def random_line(df):
	line = df.iloc[random.randrange(len(df))]
	return f"Line {line.iloc[0]}, {line.Character}: \"{line.Line}\""

def word_cloud(df):
	words = ""
	for line in df["Line"]:
		words = " ".join([words, line])
	wordcloud = WordCloud(background_color='white').generate(words)
	fig = px.imshow(wordcloud.to_image())
	fig.update_xaxes(showticklabels=False)
	fig.update_yaxes(showticklabels=False)
	return fig

def word_count(df):
	words = df.groupby("Character").sum().sort_values("Word count", ascending = False)
	#return px.bar(words, x=words.index, y=words["Word count"])
	return px.bar(df, x="Character", y="Word count", color="Word count", hover_data=df.columns)

def filtered_dataframe(f_characters):
	filtered = df.copy()
	filtered = filtered[filtered.Character.isin(f_characters)]
	return filtered


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1('Pulp Fiction'),

	html.Div(children='''
        Exploratory interactive visualization to the dialogue of Pulp Fiction
    '''),

	html.Div(
		children=random_line(df),
		id='random-line',
		style={
			'text-align': 'right'
		}),

    dcc.Graph(
        id='word-count',
        figure=word_count(df)
    ),

	dcc.Graph(
		id='word-cloud',
		figure=word_cloud(df)
	),

	dcc.Checklist(
		id='filter_characters',
    	options=characters_checkboxes(),
		value=df.Character.values
	)
])

@app.callback(
	[Output(component_id='word-count', component_property='figure'),
	 Output(component_id='random-line', component_property='children'),
	 Output(component_id='word-cloud', component_property='figure')],
	[Input(component_id='filter_characters', component_property='value')]
)
def filter_graphs(f_characters):
	f = filtered_dataframe(f_characters)
	return word_count(f), random_line(f), word_cloud(f)

if __name__ == '__main__':
    app.run_server(debug=True)