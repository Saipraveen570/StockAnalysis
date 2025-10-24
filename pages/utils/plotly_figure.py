import plotly.graph_objects as go
import pandas as pd
import numpy as np
import ta
import streamlit as st

# ------------------------------------------------------
# 1️⃣ BASIC TABLE
# ------------------------------------------------------
def plotly_table(df: pd.DataFrame):
    """Display pandas DataFrame as a clean Plotly table."""
    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=list(df.reset_index().columns),
                    fill_color="#0078FF",
                    align="center",
                    font=dict(color="white", size=13),
                    height=30,
                ),
                cells=dict(
                    values=[df.reset_index()[col] for col in df.reset_index().columns],
                    fill_color="#F9FBFD",
                    align="center",
                    height=25,
                ),
            )
        ]
    )
    fig.update_layout(margin=dict(l=0, r=0, t=20, b=0))
    return fig

# ------------------------------------------------------
# 2️⃣ CLOSE PRICE CHART
# ------------------------------------------------------
def close_chart(data: pd.DataFrame, period: str = "1y"):
    df = data.copy()
    df = _slice_period(df, period)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Close",
                             line=dict(color="#0078FF")))
    fig.update_layout(title=f"Close Price - {period.upper()}",
                      xaxis_title="Date", yaxis_title="Price",
                      template="plotly_white", height=400)
    return fig

# ------------------------------------------------------
# 3️⃣ CANDLESTICK CHART
# ------------------------------------------------------
def candlestick(data: pd.DataFrame, period: str = "1y"):
    df = data.copy()
    df = _slice_period(df, period)

    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="Candlestick"
    )])
    fig.update_layout(title=f"Candlestick Chart - {period.upper()}",
                      xaxis_title="Date", yaxis_title="Price",
                      template="plotly_white", height=500)
    return fig

# ------------------------------------------------------
# 4️⃣ RSI INDICATOR
# ------------------------------------------------------
def RSI(data: pd.DataFrame, period: str = "1y"):
    df = data.copy()

    # Dynamic RSI window
    window = st.slider("Select RSI window (days)", min_value=5, max_value=50, value=14, key="RSI_window")
    df["RSI"] = ta.momentum.RSIIndicator(df["Close"], window=window).rsi()

    df = _slice_period(df, period)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], mode="lines", name=f"RSI ({window}-day)",
                             line=dict(color="#0078FF")))
    fig.add_hline(y=70, line=dict(color="red", dash="dot"))
    fig.add_hline(y=30, line=dict(color="green", dash="dot"))
    fig.update_layout(title=f"RSI Indicator ({window}-day)",
                      xaxis_title="Date", yaxis_title="RSI Value",
                      template="plotly_white", height=300)
    return fig

# ------------------------------------------------------
# 5️⃣ MOVING AVERAGE
# ------------------------------------------------------
def Moving_average(data: pd.DataFrame, period: str = "1y"):
    df = data.copy()
    df = _slice_period(df, period)
    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA50"] = df["Close"].rolling(50).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Close", line=dict(color="#0078FF")))
    fig.add_trace(go.Scatter(x=df.index, y=df["MA20"], mode="lines", name="MA20", line=dict(color="orange")))
    fig.add_trace(go.Scatter(x=df.index, y=df["MA50"], mode="lines", name="MA50", line=dict(color="green")))
    fig.update_layout(title="Moving Averages (20 & 50)",
                      xaxis_title="Date", yaxis_title="Price",
                      template="plotly_white", height=400)
    return fig

# ------------------------------------------------------
# 6️⃣ MACD INDICATOR
# ------------------------------------------------------
def MACD(data: pd.DataFrame, period: str = "1y"):
    df = data.copy()
    df = _slice_period(df, period)

    macd = ta.trend.MACD(df["Close"])
    df["MACD"] = macd.macd()
    df["Signal"] = macd.macd_signal()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD"], mode="lines", name="MACD", line=dict(color="#0078FF")))
    fig.add_trace(go.Scatter(x=df.index, y=df["Signal"], mode="lines", name="Signal", line=dict(color="orange")))
    fig.update_layout(title="MACD Indicator",
                      xaxis_title="Date", yaxis_title="MACD Value",
                      template="plotly_white", height=300)
    return fig

# ------------------------------------------------------
# 7️⃣ FORECAST CHART
# ------------------------------------------------------
def Moving_average_forecast(data: pd.DataFrame):
    df = data.copy()
    df["MA7"] = df["Close"].rolling(7).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Actual", line=dict(color="#0078FF")))
    fig.add_trace(go.Scatter(x=df.index, y=df["MA7"], mode="lines", name="7-Day MA Forecast",
                             line=dict(color="orange", dash="dash")))
    fig.update_layout(title="30-Day Forecast with 7-Day Moving Average",
                      xaxis_title="Date", yaxis_title="Close Price",
                      template="plotly_white", height=450)
    return fig

# ------------------------------------------------------
# 8️⃣ HELPER FUNCTION TO SLICE DATA BY PERIOD
# ------------------------------------------------------
def _slice_period(df: pd.DataFrame, period: str):
    """Slice DataFrame by time period for plotting."""
    df_copy = df.copy()
    if period == "1y":
        df_copy = df_copy.tail(252)
    elif period == "5y":
        df_copy = df_copy.tail(1260)
    elif period.upper() == "YTD":
        df_copy = df_copy.loc[df_copy.index.year == pd.Timestamp.today().year]
    elif period.lower() == "max":
        pass  # full dataset
    return df_copy
