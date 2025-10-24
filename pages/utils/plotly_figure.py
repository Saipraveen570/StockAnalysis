import plotly.graph_objects as go
import pandas as pd
import numpy as np
import ta

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
# 2️⃣ PRICE CHARTS
# ------------------------------------------------------
def close_chart(data: pd.DataFrame, period: str = "1y"):
    """Line chart of closing prices."""
    df = data.copy().tail(252 if period == "1y" else len(data))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Close"))
    fig.update_layout(
        title=f"Close Price - {period.upper()}",
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_white",
        height=400,
    )
    return fig


def candlestick(data: pd.DataFrame, period: str = "1y"):
    """Candlestick chart for stock price."""
    df = data.copy().tail(252 if period == "1y" else len(data))
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df.index,
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                name="Candlestick",
            )
        ]
    )
    fig.update_layout(
        title=f"Candlestick Chart - {period.upper()}",
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_white",
        height=500,
    )
    return fig


# ------------------------------------------------------
# 3️⃣ TECHNICAL INDICATORS
# ------------------------------------------------------
def RSI(data: pd.DataFrame, period: str = "1y", window: int = 14):
    """Relative Strength Index (RSI) chart."""
    df = data.copy().tail(252 if period == "1y" else len(data))
    df["RSI"] = ta.momentum.RSIIndicator(df["Close"], window=window).rsi()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], mode="lines", name="RSI", line=dict(color="#0078FF")))
    fig.add_hline(y=70, line=dict(color="red", dash="dot"))
    fig.add_hline(y=30, line=dict(color="green", dash="dot"))
    fig.update_layout(
        title=f"RSI Indicator ({window}-day)",
        xaxis_title="Date",
        yaxis_title="RSI Value",
        template="plotly_white",
        height=300,
    )
    return fig


def Moving_average(data: pd.DataFrame, period: str = "1y"):
    """Line chart with moving averages."""
    df = data.copy().tail(252 if period == "1y" else len(data))
    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA50"] = df["Close"].rolling(50).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Close", line=dict(color="#0078FF")))
    fig.add_trace(go.Scatter(x=df.index, y=df["MA20"], mode="lines", name="MA20", line=dict(color="orange")))
    fig.add_trace(go.Scatter(x=df.index, y=df["MA50"], mode="lines", name="MA50", line=dict(color="green")))
    fig.update_layout(
        title="Moving Averages (20 & 50)",
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_white",
        height=400,
    )
    return fig


def MACD(data: pd.DataFrame, period: str = "1y"):
    """MACD chart."""
    df = data.copy().tail(252 if period == "1y" else len(data))
    macd = ta.trend.MACD(df["Close"])
    df["MACD"] = macd.macd()
    df["Signal"] = macd.macd_signal()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD"], mode="lines", name="MACD", line=dict(color="#0078FF")))
    fig.add_trace(go.Scatter(x=df.index, y=df["Signal"], mode="lines", name="Signal", line=dict(color="orange")))
    fig.update_layout(
        title="MACD Indicator",
        xaxis_title="Date",
        yaxis_title="MACD Value",
        template="plotly_white",
        height=300,
    )
    return fig


# ------------------------------------------------------
# 4️⃣ FORECAST VISUALIZATION
# ------------------------------------------------------
def Moving_average_forecast(data: pd.DataFrame):
    """Forecast chart overlay (actual + forecast)."""
    df = data.copy()
    df["MA7"] = df["Close"].rolling(7).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Actual", line=dict(color="#0078FF")))
    fig.add_trace(go.Scatter(x=df.index, y=df["MA7"], mode="lines", name="7-Day MA Forecast", line=dict(color="orange", dash="dash")))

    fig.update_layout(
        title="30-Day Forecast with 7-Day Moving Average",
        xaxis_title="Date",
        yaxis_title="Close Price",
        template="plotly_white",
        height=450,
    )
    return fig
