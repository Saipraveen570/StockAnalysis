# pages/utils/plotly_figure.py
import plotly.graph_objects as go
import pandas as pd
import ta
from typing import Optional

# -------------------------------------------
# Safe datetime normalization utility
# -------------------------------------------
def _ensure_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    try:
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index, errors="coerce")
        df = df.loc[~df.index.isna()]
    except Exception:
        return pd.DataFrame()

    return df


# -------------------------------------------
# Calendar-aware slicing with fallback
# -------------------------------------------
def _slice_period(df: pd.DataFrame, period: str) -> pd.DataFrame:
    df = _ensure_datetime_index(df)
    if df.empty:
        return df

    period = (period or "1Y").upper()
    today = pd.Timestamp.today().normalize()

    try:
        if period == "MAX":
            sliced = df
        elif period == "5D":
            start = today - pd.Timedelta(days=7)
            sliced = df.loc[df.index >= start]
        elif period == "1M":
            start = today - pd.Timedelta(days=30)
            sliced = df.loc[df.index >= start]
        elif period == "6M":
            start = today - pd.Timedelta(days=182)
            sliced = df.loc[df.index >= start]
        elif period == "YTD":
            start = pd.Timestamp(year=today.year, month=1, day=1)
            sliced = df.loc[df.index >= start]
        elif period == "1Y":
            start = today - pd.Timedelta(days=365)
            sliced = df.loc[df.index >= start]
        elif period == "5Y":
            start = today - pd.Timedelta(days=365 * 5)
            sliced = df.loc[df.index >= start]
        else:
            start = today - pd.Timedelta(days=365)
            sliced = df.loc[df.index >= start]

        if sliced.empty:
            sliced = df.tail(252)
        return sliced

    except Exception:
        return df.tail(252)


# -------------------------------------------
# Safe Plotly Table
# -------------------------------------------
def plotly_table(df: pd.DataFrame):
    if df is None:
        df = pd.DataFrame()

    try:
        if not df.index.name and not isinstance(df.index, pd.RangeIndex):
            df = df.reset_index()

        disp = df.copy()

        for col in disp.select_dtypes(include=["float", "int"]).columns:
            disp[col] = disp[col].round(4)

        fig = go.Figure(data=[
            go.Table(
                header=dict(
                    values=list(disp.columns),
                    fill_color="#0078FF",
                    align="center",
                    font=dict(color="white", size=13),
                    height=28,
                ),
                cells=dict(
                    values=[disp[c].astype(str).tolist() for c in disp.columns],
                    fill_color="#F8FAFF",
                    align="center",
                    height=24,
                ),
            )
        ])
        fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=350)
        return fig

    except Exception:
        return go.Figure()


# -------------------------------------------
# RSI
# -------------------------------------------
def RSI(data: pd.DataFrame, period: str = "1Y", window: int = 14):
    df = _ensure_datetime_index(data)
    if df.empty or "Close" not in df.columns:
        return go.Figure()

    df["Close"] = df["Close"].ffill().bfill()

    try:
        rsi_vals = ta.momentum.RSIIndicator(df["Close"], window=window).rsi().fillna(50)
    except Exception:
        rsi_vals = pd.Series(50, index=df.index)

    df["RSI"] = rsi_vals
    df = _slice_period(df, period)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], mode="lines", name=f"RSI({window})", line=dict(width=2)))
    fig.add_hrect(y0=30, y1=70, fillcolor="lightgray", opacity=0.2, line_width=0)
    fig.add_hline(y=70, line=dict(dash="dot"))
    fig.add_hline(y=30, line=dict(dash="dot"))

    fig.update_layout(
        title=f"RSI ({window})",
        template="plotly_white",
        height=300,
        yaxis_title="RSI",
        xaxis=dict(type="date"),
    )
    return fig


# -------------------------------------------
# Close + Volume
# -------------------------------------------
def close_chart(data: pd.DataFrame, period: str = "1Y"):
    df = _slice_period(data, period)
    if df.empty:
        return go.Figure()

    for col in ["Close", "Volume"]:
        if col not in df.columns:
            df[col] = 0

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Close", line=dict(width=2)))
    fig.add_trace(go.Bar(x=df.index, y=df["Volume"], opacity=0.3, name="Volume", yaxis="y2"))

    fig.update_layout(
        title="Close Price + Volume",
        template="plotly_white",
        height=450,
        yaxis=dict(title="Price"),
        yaxis2=dict(overlaying="y", side="right", title="Volume", showgrid=False),
        legend=dict(orientation="h"),
        xaxis=dict(type="date"),
        margin=dict(t=40, b=40, l=20, r=20),
    )
    return fig


# -------------------------------------------
# Moving Average (SMA + EMA)
# -------------------------------------------
def Moving_average(data: pd.DataFrame, period: str = "1Y"):
    df = _slice_period(data, period)
    if df.empty or "Close" not in df.columns:
        return go.Figure()

    df["Close"] = df["Close"].ffill().bfill()

    df["SMA20"] = df["Close"].rolling(window=20, min_periods=1).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Close"))
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA20"], name="SMA20"))
    fig.add_trace(go.Scatter(x=df.index, y=df["EMA50"], name="EMA50"))

    fig.update_layout(
        title="Moving Average",
        template="plotly_white",
        height=450,
        xaxis=dict(type="date"),
        margin=dict(t=40, b=40, l=20, r=20),
    )
    return fig


# -------------------------------------------
# MACD
# -------------------------------------------
def MACD(data: pd.DataFrame, period: str = "1Y"):
    df = _slice_period(data, period)
    if df.empty or "Close" not in df.columns:
        return go.Figure()

    df["Close"] = df["Close"].ffill().bfill()

    try:
        macd = ta.trend.MACD(df["Close"])
        df["MACD"] = macd.macd().fillna(0)
        df["Signal"] = macd.macd_signal().fillna(0)
        df["Hist"] = macd.macd_diff().fillna(0)
    except Exception:
        df["MACD"] = 0
        df["Signal"] = 0
        df["Hist"] = 0

    fig = go.Figure()
    fig.add_trace(go.Bar(x=df.index, y=df["Hist"], opacity=0.3, name="Hist"))
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD"], name="MACD"))
    fig.add_trace(go.Scatter(x=df.index, y=df["Signal"], name="Signal"))

    fig.update_layout(
        title="MACD",
        template="plotly_white",
        height=350,
        xaxis=dict(type="date"),
        margin=dict(t=40, b=40, l=20, r=20),
    )
    return fig


# -------------------------------------------
# Candlestick
# -------------------------------------------
def candlestick(data: pd.DataFrame, period: str = "1Y"):
    df = _slice_period(data, period)
    if df.empty:
        return go.Figure()

    for col in ["Open", "High", "Low", "Close"]:
        if col not in df.columns:
            df[col] = df.get("Close", 0)

    vol = df.get("Volume", pd.Series(0, index=df.index))

    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="Candles"
    ))
    fig.add_trace(go.Bar(x=df.index, y=vol, opacity=0.25, name="Volume", yaxis="y2"))

    fig.update_layout(
        title="Candlestick",
        template="plotly_white",
        height=450,
        yaxis=dict(title="Price"),
        yaxis2=dict(overlaying="y", side="right", title="Volume", showgrid=False),
        legend=dict(orientation="h"),
        xaxis=dict(type="date"),
        margin=dict(t=40, b=40, l=20, r=20),
    )
    return fig


# -------------------------------------------
# Moving Average Forecast (simple)
# -------------------------------------------
def Moving_average_forecast(df: pd.DataFrame):
    df = _ensure_datetime_index(df)
    if df.empty or "Close" not in df.columns:
        return go.Figure()

    ma7 = df.get("MA7")
    if ma7 is None:
        ma7 = df["Close"].rolling(window=7, min_periods=1).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Close"))
    fig.add_trace(go.Scatter(x=df.index, y=ma7, name="7-day MA"))

    fig.update_layout(
        title="Forecast (MA)",
        height=350,
        template="plotly_white",
        xaxis=dict(type="date")
    )
    return fig
