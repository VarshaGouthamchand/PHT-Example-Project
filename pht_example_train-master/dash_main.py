import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash_extensions import Download
from dash_extensions.snippets import send_data_frame
from dash import dash_table
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
import requests
from io import StringIO
import numpy as np
import json
import os

output_dict = {}
output_dir = "C:\\Users\\P70070487\\Downloads\\Output\\" #change this
option = []
key = ""

for filename in os.listdir(output_dir):
    if filename.endswith(".json"):
        #print(filename)
        with open(output_dir+filename) as j1:
            j1data = j1.read()
            key = str(os.path.splitext(filename)[0])
            output_dict[key] = json.loads(j1data)
            option.append({'label': key, 'value': key})
files = output_dict.keys()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app.layout = html.Div([
html.H5("Nodes:"),
    dcc.Checklist(
        id='dataset',
        options=option,
        value=[list(files)[0]],
        labelStyle={'display': 'inline-block'}
    ),
    dcc.Loading(
        id="loading-2",
        children=[html.Div([html.Div(id="loading-output-2")])],
        type="default"
    ),
    html.Div([
        html.H5("Choose an option:"),
        dcc.Dropdown(
            id='columns',
            value='Tstage',
            options=[{'label': 'Gender', 'value': 'Gender'},
                    {'label': 'T-stage', 'value': 'Tstage'},
                    {'label': 'N-stage', 'value': 'Nstage'},
                    {'label': 'M-stage', 'value': 'Mstage'},
                    {'label': 'HPV Status', 'value': 'HPV'},
                    {'label': 'Vital status', 'value': 'Survival'},
                    {'label': 'Cancer subsite', 'value': 'TumourLocation'},
                    {'label': 'Therapy', 'value': 'Therapy'}],
            clearable=False,
            style={'width': '220px'}),
        html.Div(children=[
            dcc.Graph(id="pie-chart")])
    ]),
    html.Div(children=[
        #dcc.Graph(id="sunburst"),
        dcc.Graph(id="scatter", style={"width": 500, "margin": 0, 'display': 'inline-block'}),
        dcc.Graph(id="box", style={"width": 500, "margin": 0, 'display': 'inline-block'}),
    ]),
    html.Div([
        html.Button('Click to download Demographics', id='table-but', n_clicks=0),
        #html.Div(id='container-button-basic')
        Download(id="download-dataframe-csv")
    ])
    ])

@app.callback(
    Output("pie-chart", "figure"),  
    [Input("dataset", "value"),
     Input("columns", "value")])
def generate_chart(dataset, columns):
    jsonfile = {}
    jsonfile[columns] = {}
    if dataset:
        for d in dataset:
            for key in dict(output_dict[d][columns].items()):
                if key not in jsonfile[columns]:
                    jsonfile[columns][key] = 0
                jsonfile[columns][key] += output_dict[d][columns][key]
        if (jsonfile[columns] != None):
            fig = px.pie(jsonfile, names=list(jsonfile[columns].keys()),values=list(jsonfile[columns].values()), color_discrete_sequence=px.colors.sequential.RdBu)
            return fig
        else:
            fig = px.pie(None)
            return fig
    else:
        fig = px.pie(None)
        return fig

@app.callback(
    Output("scatter", "figure"),
    [Input("dataset", "value"),
     Input("columns", "value")])
def update_scatter(dataset, columns):
    jsonfile = {}
    jsonfile['AgeRange'] = {}
    if dataset:
        for d in dataset:
            for key in dict(output_dict[d]['AgeRange'].items()):
                if key not in jsonfile['AgeRange']:
                    jsonfile['AgeRange'][key] = 0
                jsonfile['AgeRange'][key] += output_dict[d]['AgeRange'][key]
        if (jsonfile['AgeRange'] != None):
            fig = px.scatter(jsonfile, color_discrete_sequence=px.colors.qualitative.Antique, size='value', color='value')
            fig.update_layout(title_text='Cases per Age_range', title_x=0.5)
            fig.update_traces(hovertemplate='AgeRange: %{x} <br>Count: %{y}')
            return fig
        else:
            fig = px.scatter(None)
            return fig
    else:
        fig = px.scatter(None)
        return fig

@app.callback(
    Output("box", "figure"),
    [Input("dataset", "value"),
     Input("columns", "value")])
def update_box(dataset, columns):
    jsonfile = {}
    jsonfile['AgewiseMeanSurvival'] = {}
    if dataset:
        for d in dataset:
            for key in dict(output_dict[d]['AverageSurvivalbyAge'].items()):
                if key not in jsonfile['AgewiseMeanSurvival']:
                    jsonfile['AgewiseMeanSurvival'][key] = 0
                output_dict[d]['AverageSurvivalbyAge'] = {k:v if not np.isnan(v) else 0 for k,v in output_dict[d]['AverageSurvivalbyAge'].items()}
                jsonfile['AgewiseMeanSurvival'][key] += output_dict[d]['AverageSurvivalbyAge'][key]
        if (jsonfile['AgewiseMeanSurvival'] != None):
            fig = px.histogram(jsonfile, x=jsonfile['AgewiseMeanSurvival'].keys(), y=jsonfile['AgewiseMeanSurvival'].values(), color=jsonfile['AgewiseMeanSurvival'].keys())
            fig.update_layout(title_text='Survival days by age', title_x=0.5, autosize=False, width=700, height=450)
            fig.update_traces(hovertemplate='Age-Range: %{x} <br>Average Survival Days: %{y}')
            fig.update_yaxes(title='Average-Survival', visible=True, showticklabels=True)
            fig.update_xaxes(title='Age-Range', visible=True, showticklabels=True)
            return fig
        else:
            fig = px.histogram(None)
            return fig
    else:
        fig = px.histogram(None)
        return fig

@app.callback(
    #Output('container-button-basic', 'children'),
    Output("download-dataframe-csv", "data"),
    Input('table-but', 'n_clicks'),
    prevent_initial_call=True,)

def search_fi(n_clicks):
    if n_clicks > 0:
        dict_json = {}
        for file in files:
            dict_json[file] = output_dict[file]
        data = np.column_stack((np.arange(10), np.arange(10) * 10))
        df = pd.DataFrame(dict_json)
        df = df.astype(str)
        df = df.replace({'{':''}, regex=True)
        df = df.replace({'}':''}, regex=True)
        #df = df.drop(index='AjccSex', axis=1)
        #df = df.drop(index='Gender-AJCC-wise-HPV', axis=1)
        #df = df.drop(index='AgeRange', axis=1)
        #return dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, index=True)
        return send_data_frame(df.to_csv, "mydf.csv")

app.run_server(debug=True)
    