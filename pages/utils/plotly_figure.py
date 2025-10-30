# pages/utils/plotly_figure.py
import plotly.graph_objects as go
import pandas as pd
import ta
from typing import Optional

# ---------------------------
# Utility: normalize & slice
# ---------------------------
def _ensure_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of df with a DatetimeIndex. Non-convertible indices are coerced."""
    df = df.copy()
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index, errors="coerce")
    df = df.loc[~df.index.isna()]
    return df


def _slice_period(df: pd.DataFrame, period: str) -> pd.DataFrame:
    """
    Slice dataframe according to a friendly period token.
    Uses calendar-aware slicing rather than simple .tail() so weekly/monthly
    counts are more robust across missing days/markets.
    """
    df = _ensure_datetime_index(df)
    period = (period or "1Y").upper()

    today = pd.Timestamp.today().normalize()

    if period == "MAX":
        return df
    if period == "5D":
        start = today - pd.Timedelta(days=7)  # buffer for weekends
    elif period == "1M":
        start = today - pd.Timedelta(days=30)
    elif period == "6M":
        start = today - pd.Timedelta(days=182)
    elif period == "YTD":
        start = pd.Timestamp(year=today.year, month=1, day=1)
    elif period == "1Y":
        start = today - pd.Timedelta(days=365)
    elif period == "5Y":
        start = today - pd.Timedelta(days=365 * 5)
    else:
        # fallback: 1 year
        start = today - pd.Timedelta(days=365)

    sliced = df.loc[df.index >= start]
    # if slicing results empty, fall back to last available rows (best-effort)
    if sliced.empty and not df.empty:
        sliced = df.tail(252)
    return sliced


# ---------------------------
# Table
# ---------------------------
def plotly_table(df: pd.DataFrame):
    """
    Renders a Plotly table from a DataFrame.
    Keeps the index as a column if it's not already.
    """
    if df is None:
        df = pd.DataFrame()

    if not df.index.name and not isinstance(df.index, pd.RangeIndex):
        df = df.reset_index()

    # Convert all columns to strings for safe display and preserve order
    display_df = df.copy()
    # Shorten long floats
    for col in display_df.select_dtypes(include=["float", "int"]).columns:
        display_df[col] = display_df[col].round(4)

    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=list(display_df.columns),
                    fill_color="#0078FF",
                    align="center",
                    font=dict(color="white", size=13),
                    height=28,
                ),
                cells=dict(
                    values=[display_df[c].astype(str).tolist() for c in display_df.columns],
                    fill_color="#F8FAFF",
                    align="center",
                    height=24,
                ),
            )
        ]
    )
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=350)
    return fig


# ---------------------------
# RSI
# ---------------------------
def RSI(data: pd.DataFrame, period: str = "1Y", window: int = 14):
    df = data.copy()
    df = _ensure_datetime_index(df)

    if "Close" not in df.columns:
        raise ValueError("RSI requires 'Close' column in dataframe")

    # forward/backfill to avoid ta errors on small gaps
    df["Close"] = df["Close"].ffill().bfill()

    try:
        rsi_series = ta.momentum.RSIIndicator(df["Close"], window=window).rsi()
    except Exception:
        # safe fallback: constant 50
        rsi_series = pd.Series(50, index=df.index)

    df["RSI"] = rsi_series.fillna(50)
    df = _slice_period(df, period)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["RSI"],
            mode="lines",
            name=f"RSI ({window})",
            line=dict(width=2),
        )
    )

    fig.add_hrect(y0=30, y1=70, fillcolor="lightgray", opacity=0.2, line_width=0)
    fig.add_hline(y=70, line=dict(dash="dot"))
    fig.add_hline(y=30, line=dict(dash="dot"))

    fig.update_layout(
        title=f"RSI ({window}-period)",
        template="plotly_white",
        height=300,
        yaxis_title="RSI",
        xaxis=dict(type="date"),
    )
    return fig


# ---------------------------
# Close Chart + Volume
# ---------------------------
def close_chart(data: pd.DataFrame, period: str = "1Y"):
    df = data.copy()
    df = _slice_period(df, period)

    if df.empty:
        return go.Figure()

    # Ensure required columns exist
    for col in ["Close", "Volume"]:
        if col not in df.columns:
            df[col] = 0

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df.index, y=df["Close"], mode="lines", name="Close", line=dict(width=2)
        )
    )
    fig.add_trace(
        go.Bar(x=df.index, y=df["Volume"], name="Volume", opacity=0.3, yaxis="y2")
    )

    fig.update_layout(
        title="Close Price + Volume",
        template="plotly_white",
        height=450,
        yaxis=dict(title="Price"),
        yaxis2=dict(overlaying="y", side="right", showgrid=False, title="Volume"),
        legend=dict(orientation="h"),
        xaxis=dict(type="date"),
        margin=dict(t=40, b=40, l=20, r=20),
    )
    return fig


# ---------------------------
# Moving Average (SMA + EMA)
# ---------------------------
def Moving_average(data: pd.DataFrame, period: str = "1Y"):
    df = data.copy()
    df = _slice_period(df, period)

    if df.empty:
        return go.Figure()

    df["Close"] = df["Close"].ffill().bfill()

    df["SMA20"] = df["Close"].rolling(window=20, min_periods=1).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Close", line=dict(width=2))
    )
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA20"], mode="lines", name="SMA 20"))
    fig.add_trace(go.Scatter(x=df.index, y=df["EMA50"], mode="lines", name="EMA 50"))

    fig.update_layout(
        title="Moving Average (SMA & EMA)",
        template="plotly_white",
        height=450,
        xaxis=dict(type="date"),
        margin=dict(t=40, b=40, l=20, r=20),
    )
    return fig


# ---------------------------
# MACD with Histogram
# ---------------------------
def MACD(data: pd.DataFrame, period: str = "1Y"):
    df = data.copy()
    df = _slice_period(df, period)

    if df.empty:
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
    fig.add_trace(go.Bar(x=df.index, y=df["Hist"], name="Histogram", opacity=0.3))
    fig.add_trace(
        go.Scatter(x=df.index, y=df["MACD"], mode="lines", name="MACD", line=dict(width=2))
    )
    fig.add_trace(go.Scatter(x=df.index, y=df["Signal"], mode="lines", name="Signal"))

    fig.update_layout(
        title="MACD",
        template="plotly_white",
        height=350,
        xaxis=dict(type="date"),
        margin=dict(t=40, b=40, l=20, r=20),
    )
    return fig


# ---------------------------
# Candlestick + Volume
# ---------------------------
def candlestick(data: pd.DataFrame, period: str = "1Y"):
    df = data.copy()
    df = _slice_period(df, period)

    if df.empty:
        return go.Figure()

    # Ensure OHLC columns exist; if missing, fallback to Close as flat candle (best-effort)
    for col in ["Open", "High", "Low", "Close"]:
        if col not in df.columns:
            df[col] = df["Close"] if "Close" in df.columns else 0

    fig = go.Figure()
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Candles",
        )
    )
    # Volume on secondary axis
    vol_y = df["Volume"] if "Volume" in df.columns else pd.Series(0, index=df.index)
    fig.add_trace(go.Bar(x=df.index, y=vol_y, opacity=0.25, name="Volume", yaxis="y2"))

    fig.update_layout(
        title="Candlestick Chart",
        template="plotly_white",
        height=450,
        yaxis=dict(title="Price"),
        yaxis2=dict(overlaying="y", side="right", title="Volume", showgrid=False),
        legend=dict(orientation="h"),
        xaxis=dict(type="date"),
        margin=dict(t=40, b=40, l=20, r=20),
    )
    return fig


# ---------------------------
# Forecast MA Chart (helper)
# ---------------------------
def Moving_average_forecast(df: pd.DataFrame):
    """
    Simple MA forecast visualizer: expects 'Close' and optional 'MA7' in df.
    """
    df = _ensure_datetime_index(df)
    if df.empty:
        return go.Figure()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Close"))
    ma7 = df.get("MA7", None)
    if ma7 is None:
        ma7 = df["Close"].rolling(window=7, min_periods=1).mean()
    fig.add_trace(go.Scatter(x=df.index, y=ma7, name="7-day MA"))
    fig.update_layout(title="Forecast (MA)", height=350, template="plotly_white", xaxis=dict(type="date"))
    return fig
