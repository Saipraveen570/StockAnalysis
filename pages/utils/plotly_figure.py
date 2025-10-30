import plotly.graph_objects as go
import pandas as pd
import ta

# ============================
# Period Slicing
# ============================
def _slice_period(df: pd.DataFrame, period: str):
    df = df.copy()
    period = period.upper()

    if period == "5D":
        df = df.tail(5)
    elif period == "1M":
        df = df.tail(21)
    elif period == "6M":
        df = df.tail(126)
    elif period == "YTD":
        df = df[df.index.year == pd.Timestamp.today().year]
    elif period == "1Y":
        df = df.tail(252)
    elif period == "5Y":
        df = df.tail(1260)
    elif period == "MAX":
        pass

    return df

# ============================
# Table
# ============================
def plotly_table(df: pd.DataFrame):
    df = df.reset_index()
    fig = go.Figure(data=[
        go.Table(
            header=dict(
                values=list(df.columns),
                fill_color="#0078FF",
                align="center",
                font=dict(color="white", size=13),
                height=28
            ),
            cells=dict(
                values=[df[col] for col in df.columns],
                fill_color="#F8FAFF",
                align="center",
                height=24
            )
        )
    ])
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    return fig

# ============================
# RSI
# ============================
def RSI(data, period="1Y", window=14):
    df = data.copy()
    df["RSI"] = ta.momentum.RSIIndicator(df["Close"], window=window).rsi().fillna(50)
    df = _slice_period(df, period)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], mode="lines", name=f"RSI ({window})", line=dict(width=2)))

    fig.add_hrect(y0=30, y1=70, fillcolor="lightgray", opacity=0.2, line_width=0)
    fig.add_hline(y=70, line=dict(dash="dot"))
    fig.add_hline(y=30, line=dict(dash="dot"))

    fig.update_layout(
        title=f"RSI ({window}-period)",
        template="plotly_white",
        height=300,
        yaxis_title="RSI"
    )
    return fig

# ============================
# Close Chart + Volume
# ============================
def close_chart(data, period="1Y"):
    df = _slice_period(data, period)

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close', line=dict(width=2)))

    fig.add_trace(
        go.Bar(x=df.index, y=df["Volume"], name="Volume", opacity=0.3, yaxis="y2")
    )

    fig.update_layout(
        title="Close Price + Volume",
        template="plotly_white",
        height=450,
        yaxis=dict(title="Price"),
        yaxis2=dict(overlaying="y", side="right", showgrid=False, title="Volume"),
        legend=dict(orientation="h")
    )
    return fig

# ============================
# Moving Average (SMA + EMA)
# ============================
def Moving_average(data, period="1Y"):
    df = _slice_period(data, period)

    df['SMA20'] = df['Close'].rolling(20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close', line=dict(width=2)))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], mode='lines', name='SMA 20'))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], mode='lines', name='EMA 50'))

    fig.update_layout(
        title="Moving Average (SMA & EMA)",
        template="plotly_white",
        height=450
    )
    return fig

# ============================
# MACD with Histogram
# ============================
def MACD(data, period="1Y"):
    df = _slice_period(data, period)

    macd = ta.trend.MACD(df['Close'])
    df['MACD'] = macd.macd().fillna(0)
    df['Signal'] = macd.macd_signal().fillna(0)
    df['Hist'] = macd.macd_diff().fillna(0)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=df.index, y=df["Hist"], name="Histogram", opacity=0.3))
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], mode='lines', name='MACD', line=dict(width=2)))
    fig.add_trace(go.Scatter(x=df.index, y=df['Signal'], mode='lines', name='Signal'))

    fig.update_layout(
        title="MACD",
        template="plotly_white",
        height=350
    )
    return fig

# ============================
# Candlestick + Volume
# ============================
def candlestick(data, period="1Y"):
    df = _slice_period(data, period)

    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            name="Candles"
        )
    )

    fig.add_trace(
        go.Bar(x=df.index, y=df['Volume'], opacity=0.25, name="Volume", yaxis="y2")
    )

    fig.update_layout(
        title="Candlestick Chart",
        template="plotly_white",
        height=450,
        yaxis=dict(title="Price"),
        yaxis2=dict(overlaying="y", side="right", title="Volume", showgrid=False),
        legend=dict(orientation="h")
    )
    return fig

# ============================
# Forecast MA Chart
# ============================
def Moving_average_forecast(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Close'))
    fig.add_trace(go.Scatter(x=df.index, y=df.get('MA7', df['Close']), name='7-day MA'))
    fig.update_layout(title='Forecast (MA)', height=350, template="plotly_white")
    return fig
