import plotly.graph_objects as go
import pandas as pd
import ta  # Technical Analysis library


# =========================
# 📊 CANDLESTICK CHART
# =========================
def candlestick(data):
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=data.index,
                open=data["Open"],
                high=data["High"],
                low=data["Low"],
                close=data["Close"],
                name="Candlestick",
            )
        ]
    )

    fig.update_layout(
        title="📈 Candlestick Chart",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        template="plotly_white",
        height=500,
    )
    return fig


# =========================
# 📈 MOVING AVERAGE (MA)
# =========================
def Moving_average(data, short_window=20, long_window=50):
    df = data.copy()
    df["MA20"] = df["Close"].rolling(window=short_window).mean()
    df["MA50"] = df["Close"].rolling(window=long_window).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Close"))
    fig.add_trace(go.Scatter(x=df.index, y=df["MA20"], mode="lines", name="MA 20"))
    fig.add_trace(go.Scatter(x=df.index, y=df["MA50"], mode="lines", name="MA 50"))

    fig.update_layout(
        title="📊 Moving Average (MA20 vs MA50)",
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_white",
        height=500,
    )
    return fig


# =========================
# 📉 RELATIVE STRENGTH INDEX (RSI)
# =========================
def RSI(data, period=14):
    df = data.copy()
    df["RSI"] = ta.momentum.RSIIndicator(df["Close"], window=period).rsi()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], mode="lines", name="RSI"))

    fig.add_hline(y=70, line_dash="dash", line_color="red")
    fig.add_hline(y=30, line_dash="dash", line_color="green")

    fig.update_layout(
        title="📉 Relative Strength Index (RSI)",
        xaxis_title="Date",
        yaxis_title="RSI",
        template="plotly_white",
        height=400,
    )
    return fig


# =========================
# 📊 MOVING AVERAGE CONVERGENCE DIVERGENCE (MACD)
# =========================
def MACD(data, short=12, long=26, signal=9):
    df = data.copy()
    macd = ta.trend.MACD(df["Close"], window_slow=long, window_fast=short, window_sign=signal)
    df["MACD"] = macd.macd()
    df["Signal"] = macd.macd_signal()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD"], mode="lines", name="MACD"))
    fig.add_trace(go.Scatter(x=df.index, y=df["Signal"], mode="lines", name="Signal"))

    fig.update_layout(
        title="📊 MACD (Moving Average Convergence Divergence)",
        xaxis_title="Date",
        yaxis_title="MACD",
        template="plotly_white",
        height=400,
    )
    return fig
