'''
Application running on pythonanywhere
'''
from dash import Dash, dcc, html
import plotly.express as px
import pandas as pd
import numpy as np
import sqlalchemy as sa
from sqlalchemy import text

app = Dash(__name__)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

with open('mysql.txt') as f:
    mysqlp = f.read()

def getLatest():
    
    # create connection to database
    engine = sa.create_engine(f"mysql+mysqldb://busbykt:pythonanywhere@busbykt.mysql.pythonanywhere-services.com/busbykt$wxdb")

    # query for data to plot
    query = '''
    SELECT * FROM wxData ORDER BY DateTime Desc LIMIT 2
    '''
    # read in data
    df = pd.read_sql_query(query,engine)

    # convert from utc to pst
    df['DateTime'] = df['DateTime'].astype('datetime64[ns]').dt.tz_localize('utc').dt.tz_convert('US/Pacific')
    
    return df.iloc[-1]['DateTime'],df.iloc[-1]['Temperature'],df.iloc[-1]['Humidity'],df.iloc[-1]['Pressure'],df.iloc[-1]['WindSpeed'],df.iloc[-1]['WindDir'],df.iloc[-1]['BatteryVolt']


def getTempHumPress():
    
    # create connection to database
    engine = sa.create_engine(f'mysql+mysqldb://busbykt:pythonanywhere@busbykt.mysql.pythonanywhere-services.com/busbykt$wxdb')

    # query for data to plot
    query = '''
    SELECT * FROM wxData ORDER BY DateTime DESC LIMIT 4000
    '''
    
    # read in data
    df = pd.read_sql_query(query,engine)
    
    # localize time
    df['DateTime'] = df['DateTime'].astype('datetime64[ns]')
    df['DateTime'] = df['DateTime'].dt.tz_localize('utc').dt.tz_convert('US/Pacific')

    return df

def graphWindSpdDir(df):


    # convert wind directions to numeric
    df['WindDir'] = df['WindDir'].replace({
        'N':0,
        'NNE':22.5,
        'NE':22.5*2,
        'ENE':22.5*3,
        'E':90,
        'ESE':22.5*5,
        'SE':22.5*6,
        'SSE':22.5*7,
        'S':180,
        'SSW':22.5*9,
        'SW':22.5*10,
        'WSW':22.5*11,
        'W':270,
        'WNW':22.5*13,
        'NW':22.5*14,
        'NNW':22.5*15
    })

    # generate a column defining how long ago a sample was
    df['secondsSince'] = (pd.to_datetime('now').tz_localize('utc').tz_convert('US/Pacific')-df['DateTime']).dt.total_seconds()

    fig = px.scatter_polar(df, r="WindSpeed", theta="WindDir", template='plotly_dark', size='secondsSince')
    
    return fig

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

def graphBattery(df):
    
    # generate the battery voltage graph
    fig = px.line(df, x='DateTime', y=['BatteryVolt'])
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text']
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    return fig

# layout the app
def serveLayout():
    
    # query for latest data
    latest = getLatest()
    
    # query for graph data
    df = getTempHumPress()
    
    sLayout = html.Div(style={'backgroundColor': colors['background']}, children=[
        html.H1(
            children='Station Conditions',
            style={
                'textAlign': 'center',
                'color': colors['text']
            }
        ),

        html.H3(children=f"{latest[0]} PST", style={
            'textAlign': 'center',
            'color': colors['text']
        }),

        html.H3(children=f"Wind {latest[5]} {latest[4]} MPH", style={
            'textAlign': 'center',
            'color': colors['text']
        }),

        html.H3(children=f"Temperature {latest[1]} F", style={
            'textAlign': 'center',
            'color': colors['text']
        }),
        
        html.H3(children=f"Humidity {latest[2]}%", style={
            'textAlign': 'center',
            'color': colors['text']
        }),
        
        html.H3(children=f"Pressure {latest[3]} mBar", style={
            'textAlign': 'center',
            'color': colors['text']
        }),

        dcc.Graph(
            id='windSpdDir',
            figure=graphWindSpdDir(df)
        ),

        dcc.Graph(
            id='tempHumGraph',
            figure=graphTempHum(df)
        ),

        dcc.Graph(
            id='pressureGraph',
            figure=graphPressure(df)
        ),
    
        dcc.Graph(
            id='batteryVoltage',
            figure=graphBattery(df)
        ),
        
        
    ])
    
    return sLayout

app.layout = serveLayout

if __name__ == '__main__':
    app.run_server()
