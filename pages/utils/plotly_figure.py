import plotly.graph_objects as go
import pandas as pd
import numpy as np
import ta

# ----------------------------
# Table Plot
# ----------------------------
def plotly_table(df):
    fig = go.Figure(data=[go.Table(
        header=dict(values=["Metric","Value"], fill_color='lightblue', align='left'),
        cells=dict(values=[df.index, df['Value']], fill_color='lavender', align='left')
    )])
    return fig

# ----------------------------
# Close Price Line Chart
# ----------------------------
def close_chart(df, period):
    df_plot = df.copy()
    if period != 'max':
        df_plot = df_plot.last(period)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['Close'], mode='lines', name='Close Price'))
    fig.update_layout(title='Close Price', xaxis_title='Date', yaxis_title='Price', template='plotly_white')
    return fig

# ----------------------------
# Candlestick Chart
# ----------------------------
def candlestick(df, period):
    df_plot = df.copy()
    if period != 'max':
        df_plot = df_plot.last(period)
    fig = go.Figure(data=[go.Candlestick(
        x=df_plot.index,
        open=df_plot['Open'],
        high=df_plot['High'],
        low=df_plot['Low'],
        close=df_plot['Close'],
        increasing_line_color='green',
        decreasing_line_color='red'
    )])
    fig.update_layout(title='Candlestick Chart', xaxis_title='Date', yaxis_title='Price', template='plotly_white')
    return fig

# ----------------------------
# RSI Chart
# ----------------------------
def RSI(df, period, window=14):
    df_plot = df.copy()
    if period != 'max':
        df_plot = df_plot.last(period)
    df_plot['RSI'] = ta.momentum.RSIIndicator(df_plot['Close'], window=window).rsi()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['RSI'], mode='lines', name='RSI'))
    fig.update_layout(title=f'RSI ({window}-day)', xaxis_title='Date', yaxis_title='RSI', template='plotly_white')
    return fig

# ----------------------------
# Moving Average
# ----------------------------
def Moving_average(df, period, window=7):
    df_plot = df.copy()
    if period != 'max':
        df_plot = df_plot.last(period)
    df_plot['MA'] = df_plot['Close'].rolling(window=window).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['Close'], mode='lines', name='Close Price'))
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['MA'], mode='lines', name=f'{window}-day MA'))
    fig.update_layout(title='Moving Average', xaxis_title='Date', yaxis_title='Price', template='plotly_white')
    return fig

# ----------------------------
# MACD
# ----------------------------
def MACD(df, period, fast=12, slow=26, signal=9):
    df_plot = df.copy()
    if period != 'max':
        df_plot = df_plot.last(period)
    exp1 = df_plot['Close'].ewm(span=fast, adjust=False).mean()
    exp2 = df_plot['Close'].ewm(span=slow, adjust=False).mean()
    df_plot['MACD'] = exp1 - exp2
    df_plot['Signal'] = df_plot['MACD'].ewm(span=signal, adjust=False).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['MACD'], mode='lines', name='MACD'))
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['Signal'], mode='lines', name='Signal'))
    fig.update_layout(title='MACD', xaxis_title='Date', yaxis_title='MACD', template='plotly_white')
    return fig
