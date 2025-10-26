import plotly.graph_objects as go
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD as MACDIndicator

def plotly_table(df: pd.DataFrame):
    fig = go.Figure(data=[go.Table(
        header=dict(values=['Metric', 'Value'], fill_color='paleturquoise', align='left'),
        cells=dict(values=[df.index, df['Value']], fill_color='lavender', align='left'))
    ])
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=300)
    return fig

def close_chart(df: pd.DataFrame, title="Close Price"):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close'))
    fig.update_layout(title=title, xaxis_title="Date", yaxis_title="Price")
    return fig

def candlestick(df: pd.DataFrame, title="Candlestick Chart"):
    fig = go.Figure(data=[go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']
    )])
    fig.update_layout(title=title, xaxis_title="Date", yaxis_title="Price")
    return fig

def RSI(df: pd.DataFrame, title="RSI", window=14):
    rsi = RSIIndicator(df['Close'], window=window).rsi()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=rsi, mode='lines', name=f'RSI ({window})'))
    fig.update_layout(title=title, xaxis_title="Date", yaxis_title="RSI")
    return fig

def Moving_average(df: pd.DataFrame, title="Moving Average"):
    ma7 = df['Close'].rolling(7).mean()
    ma30 = df['Close'].rolling(30).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close'))
    fig.add_trace(go.Scatter(x=df.index, y=ma7, mode='lines', name='MA7'))
    fig.add_trace(go.Scatter(x=df.index, y=ma30, mode='lines', name='MA30'))
    fig.update_layout(title=title, xaxis_title="Date", yaxis_title="Price")
    return fig

def MACD(df: pd.DataFrame, title="MACD"):
    macd_indicator = MACDIndicator(df['Close'])
    macd = macd_indicator.macd()
    signal = macd_indicator.macd_signal()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=macd, mode='lines', name='MACD'))
    fig.add_trace(go.Scatter(x=df.index, y=signal, mode='lines', name='Signal'))
    fig.update_layout(title=title, xaxis_title="Date", yaxis_title="Value")
    return fig

def Moving_average_forecast(df: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close'))
    if 'MA7' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['MA7'], mode='lines', name='MA7'))
    fig.update_layout(title="Close Price & MA7 Forecast", xaxis_title="Date", yaxis_title="Price")
    return fig
