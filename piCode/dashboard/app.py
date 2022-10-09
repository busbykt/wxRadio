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

def getLatest():
    
    # create connection to database
    con = sqlite3.connect('../wx.db')

    # query for data to plot
    query = '''
    SELECT Temperature,Humidity,Pressure FROM wxData ORDER BY rowid Desc LIMIT 2
    '''
    # read in data
    df = pd.read_sql_query(query,con)
    # close connection
    con.close()
    
    return df.iloc[-1]['Temperature'],df.iloc[-1]['Humidity'],df.iloc[-1]['Pressure']


def getTempHumPress():
    
    # create connection to database
    con = sqlite3.connect('../wx.db')

    # query for data to plot
    query = '''
    SELECT DateTime,Temperature,Humidity,Pressure FROM wxData ORDER BY DateTime DESC LIMIT 8000
    '''
    
    # read in data
    df = pd.read_sql_query(query,con)
    # close connection
    con.close()
    
    # localize time
    df['DateTime'] = df['DateTime'].astype('datetime64[ns]')
    df['DateTime'] = df['DateTime'].dt.tz_localize('utc').dt.tz_convert('US/Pacific')

    return df

def graphTempHum(df):
    
    
    # generate the temp/humidity graph
    fig = px.line(df, x='DateTime', y=['Temperature','Humidity'])
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text']
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    return fig

def graphPressure(df):
    
    # generate the pressure graph
    fig = px.line(df, x='DateTime', y=['Pressure'])
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text']
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    fig.update_traces(line_color='#66eb59')

    return fig

# layout the app
def serveLayout():
    
    # query for latest data
    latest = getLatest()
    
    # query for graph data
    df = getTempHumPress()
    
    sLayout = html.Div(style={'backgroundColor': colors['background']}, children=[
        html.H1(
            children='Wx Station Conditions',
            style={
                'textAlign': 'center',
                'color': colors['text']
            }
        ),

        html.H3(children=f"Temperature {latest[0]} F", style={
            'textAlign': 'center',
            'color': colors['text']
        }),
        
        html.H3(children=f"Humidity {latest[1]}%", style={
            'textAlign': 'center',
            'color': colors['text']
        }),
        
        html.H3(children=f"Pressure {latest[2]} mBar", style={
            'textAlign': 'center',
            'color': colors['text']
        }),

        dcc.Graph(
            id='tempHumGraph',
            figure=graphTempHum(df)
        ),

        dcc.Graph(
            id='pressureGraph',
            figure=graphPressure(df)
        ),
        
    ])
    
    return sLayout

app.layout = serveLayout

if __name__ == '__main__':
    app.run_server(debug=True)
