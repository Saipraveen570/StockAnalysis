import plotly.graph_objects as go
import pandas as pd
import numpy as np
import ta

# ------------------------------
# Plotly Table
# ------------------------------
def plotly_table(df):
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[df[col] for col in df.columns],
                   fill_color='lavender',
                   align='left'))
    ])
    return fig

# ------------------------------
# Candlestick Chart
# ------------------------------
def candlestick(df, period='1y'):
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Candlestick'
    )])
    fig.update_layout(title=f"Candlestick Chart ({period.upper()})", xaxis_rangeslider_visible=False)
    return fig

# ------------------------------
# Close Price Line Chart
# ------------------------------
def close_chart(df, period='1y'):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Close'],
        mode='lines',
        name='Close Price'
    ))
    fig.update_layout(title=f"Close Price Chart ({period.upper()})")
    return fig

# ------------------------------
# Moving Average Chart
# ------------------------------
def Moving_average(df, period='1y', window=7):
    df_ma = df.copy()
    df_ma['MA'] = df_ma['Close'].rolling(window=window).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_ma.index, y=df_ma['Close'], mode='lines', name='Close Price'))
    fig.add_trace(go.Scatter(x=df_ma.index, y=df_ma['MA'], mode='lines', name=f'{window}-Day MA'))
    fig.update_layout(title=f"Moving Average ({window}-Day) ({period.upper()})")
    return fig

# ------------------------------
# RSI Chart
# ------------------------------
def RSI(df, period='1y', window=14):
    df_rsi = df.copy()
    df_rsi['RSI'] = ta.momentum.RSIIndicator(df_rsi['Close'], window=window).rsi()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_rsi.index, y=df_rsi['RSI'], mode='lines', name=f'RSI ({window})'))
    fig.update_layout(title=f"Relative Strength Index ({window}-Day) ({period.upper()})", yaxis=dict(range=[0,100]))
    return fig

# ------------------------------
# MACD Chart
# ------------------------------
def MACD(df, period='1y', fast=12, slow=26, signal=9):
    df_macd = df.copy()
    macd_indicator = ta.trend.MACD(df_macd['Close'], window_slow=slow, window_fast=fast, window_sign=signal)
    df_macd['MACD'] = macd_indicator.macd()
    df_macd['Signal'] = macd_indicator.macd_signal()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_macd.index, y=df_macd['MACD'], mode='lines', name='MACD'))
    fig.add_trace(go.Scatter(x=df_macd.index, y=df_macd['Signal'], mode='lines', name='Signal'))
    fig.update_layout(title=f"MACD ({fast},{slow},{signal}) ({period.upper()})")
    return fig
