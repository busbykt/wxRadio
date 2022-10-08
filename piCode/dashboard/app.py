# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, dcc, html
import plotly.express as px
import pandas as pd
import numpy as np

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

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
fig = px.line(df, x=df.index, y=['Temperature','Humidity'])

fig.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)
fig.update_xaxes(showgrid=False)
fig.update_yaxes(showgrid=False)

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Aerial Paragliding Launch Conditions',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children=f"Temperature {df.iloc[-1]['Temperature']}", style={
        'textAlign': 'center',
        'color': colors['text']
    }),
    
    html.Div(children=f"Humidity {df.iloc[-1]['Humidity']}", style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    dcc.Graph(
        id='example-graph-2',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
