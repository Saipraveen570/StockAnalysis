import plotly.graph_objects as go
import pandas as pd

# Table plot
def plotly_table(df):
    fig = go.Figure(data=[go.Table(
        header=dict(values=["Metric", "Value"], fill_color='paleturquoise', align='left'),
        cells=dict(values=[df.index, df['Value']], fill_color='lavender', align='left')
    )])
    return fig

# Line chart
def close_chart(df, period='1y'):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close'))
    return fig

# Candlestick
def candlestick(df, period='1y'):
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close']
    )])
    return fig

# RSI
def RSI(df, period='1y', window=14):
    import ta
    rsi = ta.momentum.RSIIndicator(df['Close'], window=window).rsi()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=rsi, mode='lines', name='RSI'))
    return fig

# Moving Average
def Moving_average(df, period='1y', window=7):
    df_ma = df['Close'].rolling(window).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close'))
    fig.add_trace(go.Scatter(x=df.index, y=df_ma, mode='lines', name=f'MA-{window}'))
    return fig

# MACD
def MACD(df, period='1y', fast=12, slow=26, signal=9):
    import ta
    macd = ta.trend.MACD(df['Close'], window_slow=slow, window_fast=fast, window_sign=signal)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=macd.macd(), mode='lines', name='MACD'))
    fig.add_trace(go.Scatter(x=df.index, y=macd.macd_signal(), mode='lines', name='Signal'))
    return fig

# Moving average forecast chart
def Moving_average_forecast(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close'))
    if 'MA7' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['MA7'], mode='lines', name='MA7'))
    return fig
