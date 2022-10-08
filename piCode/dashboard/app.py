# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, dcc, html
import plotly.express as px
import pandas as pd
import numpy as np
import sqlite3

app = Dash(__name__)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

# read in data
df = pd.read_csv(
    '../wxData.csv',
    header=None,
    names=['Temperature','Humidity','Pressure']
)

# generate the temp/humidity graph
fig = px.line(df, x=df.index, y=['Temperature','Humidity'])
fig.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)
fig.update_xaxes(showgrid=False)
fig.update_yaxes(showgrid=False)

# generate the pressure graph
mbarFig = px.line(df, x=df.index, y=['Pressure'])
mbarFig.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)
mbarFig.update_xaxes(showgrid=False)
mbarFig.update_yaxes(showgrid=False)
mbarFig.update_traces(line_color='#66eb59')

# layout the app
app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Wx Station Conditions',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.H3(children=f"Temperature {df.iloc[-1]['Temperature']} F", style={
        'textAlign': 'center',
        'color': colors['text']
    }),
    
    html.H3(children=f"Humidity {df.iloc[-1]['Humidity']}%", style={
        'textAlign': 'center',
        'color': colors['text']
    }),
    
    html.H3(children=f"Pressure {df.iloc[-1]['Pressure']} mBar", style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    dcc.Graph(
        id='tempHumGraph',
        figure=fig
    ),

    dcc.Graph(
        id='pressureGraph',
        figure=mbarFig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
