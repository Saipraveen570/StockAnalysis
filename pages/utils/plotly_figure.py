import plotly.graph_objs as go
import pandas as pd
import ta

# ==========================
# TABLE DISPLAY
# ==========================
def plotly_table(df):
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns), align="left"),
        cells=dict(values=[df[col] for col in df.columns], align="left")
    )])
    fig.update_layout(height=300)
    return fig

# ==========================
# LINE CLOSE CHART
# ==========================
def close_chart(df, period="1y"):
    df = _filter_period(df, period)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Close"))
    fig.update_layout(height=400, title=f"Closing Price ({period})")
    return fig

# ==========================
# CANDLE CHART
# ==========================
def candlestick(df, period="1y"):
    df = _filter_period(df, period)
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']
    )])
    fig.update_layout(height=500, title=f"Candlestick Chart ({period})")
    return fig

# ==========================
# MOVING AVERAGE CHART
# ==========================
def Moving_average(df, period="1y"):
    df = _filter_period(df, period)
    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA50"] = df["Close"].rolling(50).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Close"))
    fig.add_trace(go.Scatter(x=df.index, y=df["MA20"], mode="lines", name="MA20"))
    fig.add_trace(go.Scatter(x=df.index, y=df["MA50"], mode="lines", name="MA50"))
    fig.update_layout(height=450, title=f"Moving Averages ({period})")
    return fig

# ==========================
# RSI INDICATOR
# ==========================
def RSI(df, period="1y"):
    df = _filter_period(df, period)
    df["RSI"] = ta.momentum.rsi(df["Close"], window=14)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], mode="lines", name="RSI"))
    fig.update_layout(height=300, title=f"RSI ({period})", yaxis=dict(range=[0,100]))
    return fig

# ==========================
# MACD INDICATOR
# ==========================
def MACD(df, period="1y"):
    df = _filter_period(df, period)
    macd = ta.trend.MACD(df["Close"])
    df["MACD"] = macd.macd()
    df["MACD_signal"] = macd.macd_signal()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD"], mode="lines", name="MACD"))
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD_signal"], mode="lines", name="Signal"))
    fig.update_layout(height=300, title=f"MACD ({period})")
    return fig

# ==========================
# MOVING AVERAGE FORECAST PLOT (for Prediction page)
# ==========================
def Moving_average_forecast(df):
    fig = go.Figure()
    if "Close" in df:    
        fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Actual"))
    if "Predicted" in df:
        fig.add_trace(go.Scatter(x=df.index, y=df["Predicted"], mode="lines", name="Predicted"))
    fig.update_layout(height=450, title="Forecast vs Actual")
    return fig

# ==========================
# HELPER FUNCTION: FILTER PERIOD
# ==========================
def _filter_period(df, period):
    if isinstance(df.index, pd.DatetimeIndex):
        if period != "max":
            df = df.last(period)
    return df
