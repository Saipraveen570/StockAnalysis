import plotly.graph_objects as go
import pandas as pd
import numpy as np
import ta

# ---------------------------
# Table Plot
# ---------------------------
def plotly_table(df):
    fig = go.Figure(data=[go.Table(
        header=dict(values=["Metric", "Value"],
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[df.index, df['Value']],
                   fill_color='lavender',
                   align='left'))
    ])
    fig.update_layout(margin=dict(t=10,b=10))
    return fig

# ---------------------------
# Close Price Line Chart
# ---------------------------
def close_chart(df, period='1y'):
    df_plot = df.copy()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['Close'], mode='lines', name='Close'))
    fig.update_layout(title="Close Price", xaxis_title="Date", yaxis_title="Price", margin=dict(t=40))
    return fig

# ---------------------------
# Candlestick Chart
# ---------------------------
def candlestick(df, period='1y'):
    df_plot = df.copy()
    fig = go.Figure(data=[go.Candlestick(
        x=df_plot.index,
        open=df_plot['Open'],
        high=df_plot['High'],
        low=df_plot['Low'],
        close=df_plot['Close'],
        name='Candlestick'
    )])
    fig.update_layout(title="Candlestick Chart", xaxis_title="Date", yaxis_title="Price", margin=dict(t=40))
    return fig

# ---------------------------
# RSI Chart (Dynamic Window)
# ---------------------------
def RSI(df, period='1y', window=14):
    df_plot = df.copy()
    df_plot['RSI'] = ta.momentum.RSIIndicator(df_plot['Close'], window=window).rsi()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['RSI'], mode='lines', name=f'RSI ({window})'))
    fig.update_layout(title=f"RSI ({window} days)", xaxis_title="Date", yaxis_title="RSI", margin=dict(t=40))
    fig.add_hline(y=70, line_dash="dash", line_color="red")
    fig.add_hline(y=30, line_dash="dash", line_color="green")
    return fig

# ---------------------------
# Moving Average Chart
# ---------------------------
def Moving_average(df, period='1y', window=20):
    df_plot = df.copy()
    df_plot[f'MA_{window}'] = df_plot['Close'].rolling(window=window).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['Close'], mode='lines', name='Close'))
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot[f'MA_{window}'], mode='lines', name=f'MA ({window})'))
    fig.update_layout(title=f"Close Price with {window}-Day Moving Average", xaxis_title="Date", yaxis_title="Price", margin=dict(t=40))
    return fig

# ---------------------------
# MACD Chart
# ---------------------------
def MACD(df, period='1y', fast=12, slow=26, signal=9):
    df_plot = df.copy()
    df_plot['MACD'] = ta.trend.MACD(df_plot['Close'], window_slow=slow, window_fast=fast, window_sign=signal).macd()
    df_plot['Signal'] = ta.trend.MACD(df_plot['Close'], window_slow=slow, window_fast=fast, window_sign=signal).macd_signal()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['MACD'], mode='lines', name='MACD'))
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['Signal'], mode='lines', name='Signal'))
    fig.update_layout(title="MACD Chart", xaxis_title="Date", yaxis_title="MACD", margin=dict(t=40))
    return fig
