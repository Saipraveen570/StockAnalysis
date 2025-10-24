import plotly.graph_objects as go
import pandas as pd
import numpy as np
import ta

# -------------------- TABLE --------------------
def plotly_table(df: pd.DataFrame):
    """Creates a simple Plotly table from a DataFrame."""
    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=list(df.columns.insert(0, df.index.name or "")),
                    fill_color="#0078ff",
                    align="center",
                    font=dict(color="white", size=13),
                ),
                cells=dict(
                    values=[df.index.tolist()] + [df[col].tolist() for col in df.columns],
                    fill_color=[["#f8f9fa"]],
                    align="center",
                    font=dict(color="black", size=12),
                ),
            )
        ]
    )
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    return fig


# -------------------- CLOSE CHART --------------------
def close_chart(data: pd.DataFrame, period: str = "1y"):
    """Simple line chart of closing prices."""
    df = data.tail(_period_to_rows(data, period))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Close", line=dict(color="#0078ff")))
    fig.update_layout(title=f"Close Price ({period})", xaxis_title="Date", yaxis_title="Price", template="plotly_white")
    return fig


# -------------------- CANDLESTICK --------------------
def candlestick(data: pd.DataFrame, period: str = "1y"):
    """Candlestick chart of stock prices."""
    df = data.tail(_period_to_rows(data, period))
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df.index,
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                increasing_line_color="#00b74a",
                decreasing_line_color="#f93154",
            )
        ]
    )
    fig.update_layout(title=f"Candlestick Chart ({period})", xaxis_title="Date", yaxis_title="Price", template="plotly_white")
    return fig


# -------------------- RSI --------------------
def RSI(data: pd.DataFrame, period: str = "1y"):
    """Relative Strength Index chart."""
    df = data.tail(_period_to_rows(data, period)).copy()
    df["RSI"] = ta.momentum.RSIIndicator(df["Close"], window=14).rsi()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], mode="lines", name="RSI", line=dict(color="#0078ff")))
    fig.add_hline(y=70, line_dash="dash", line_color="red")
    fig.add_hline(y=30, line_dash="dash", line_color="green")

    fig.update_layout(title=f"RSI ({period})", yaxis_title="RSI Value", template="plotly_white")
    return fig


# -------------------- MOVING AVERAGE --------------------
def Moving_average(data: pd.DataFrame, period: str = "1y"):
    """Close price with 7, 14, and 30-day moving averages."""
    df = data.tail(_period_to_rows(data, period)).copy()
    df["MA7"] = df["Close"].rolling(window=7).mean()
    df["MA14"] = df["Close"].rolling(window=14).mean()
    df["MA30"] = df["Close"].rolling(window=30).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Close", line=dict(color="#0078ff")))
    fig.add_trace(go.Scatter(x=df.index, y=df["MA7"], mode="lines", name="7-day MA", line=dict(color="#74b9ff")))
    fig.add_trace(go.Scatter(x=df.index, y=df["MA14"], mode="lines", name="14-day MA", line=dict(color="#00b894")))
    fig.add_trace(go.Scatter(x=df.index, y=df["MA30"], mode="lines", name="30-day MA", line=dict(color="#fdcb6e")))

    fig.update_layout(title=f"Moving Averages ({period})", xaxis_title="Date", yaxis_title="Price", template="plotly_white")
    return fig


# -------------------- MACD --------------------
def MACD(data: pd.DataFrame, period: str = "1y"):
    """MACD line, signal line, and histogram chart."""
    df = data.tail(_period_to_rows(data, period)).copy()
    macd_indicator = ta.trend.MACD(df["Close"])
    df["MACD"] = macd_indicator.macd()
    df["Signal"] = macd_indicator.macd_signal()
    df["Histogram"] = macd_indicator.macd_diff()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD"], mode="lines", name="MACD", line=dict(color="#0078ff")))
    fig.add_trace(go.Scatter(x=df.index, y=df["Signal"], mode="lines", name="Signal", line=dict(color="#ff7675")))
    fig.add_trace(go.Bar(x=df.index, y=df["Histogram"], name="Histogram", marker_color="#b2bec3", opacity=0.4))

    fig.update_layout(title=f"MACD ({period})", xaxis_title="Date", yaxis_title="Value", template="plotly_white")
    return fig


# -------------------- Helper Function --------------------
def _period_to_rows(data: pd.DataFrame, period: str) -> int:
    """Maps a period string (e.g. '1y', '6mo') to number of rows based on data frequency."""
    mapping = {
        "5d": 5,
        "1mo": 22,
        "6mo": 132,
        "ytd": 180,
        "1y": 252,
        "5y": 1260,
        "max": len(data),
    }
    return mapping.get(period, 252)
