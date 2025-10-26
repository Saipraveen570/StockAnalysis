# utils/plotly_figure.py
import plotly.graph_objects as go
import pandas as pd

def plotly_table(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[df.index, df[df.columns[0]]],
                   fill_color='lavender',
                   align='left'))
    ])
    fig.update_layout(height=300)
    return fig

def Moving_average(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close Price'))
    if 'MA7' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['MA7'], mode='lines', name='MA7'))
    fig.update_layout(title='📊 Stock Moving Average', xaxis_title='Date', yaxis_title='Price')
    return fig

def Moving_average_forecast(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close'))
    if 'MA7' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['MA7'], mode='lines', name='MA7'))
    fig.update_layout(title='🔮 Stock Forecast', xaxis_title='Date', yaxis_title='Price')
    return fig
