import plotly.graph_objects as go
import pandas as pd
import ta

# -------------------------
# Helper to slice periods
# -------------------------
def _slice_period(df: pd.DataFrame, period: str):
    df_copy = df.copy()
    if period == "1y":
        df_copy = df_copy.tail(252)
    elif period == "5y":
        df_copy = df_copy.tail(1260)
    elif period.upper() == "YTD":
        df_copy = df_copy.loc[df_copy.index.year == pd.Timestamp.today().year]
    elif period.lower() == "max":
        pass
    return df_copy

# -------------------------
# RSI Indicator
# -------------------------
def RSI(data: pd.DataFrame, period: str = "1y", window: int = 14):
    df = data.copy()
    df["RSI"] = ta.momentum.RSIIndicator(df["Close"], window=window).rsi()
    df = _slice_period(df, period)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], mode="lines",
                             name=f"RSI ({window}-day)", line=dict(color="#0078FF")))
    fig.add_hline(y=70, line=dict(color="red", dash="dot"))
    fig.add_hline(y=30, line=dict(color="green", dash="dot"))
    fig.update_layout(title=f"RSI Indicator ({window}-day)",
                      xaxis_title="Date", yaxis_title="RSI Value",
                      template="plotly_white", height=300)
    return fig

# -------------------------
# Plotly Table
# -------------------------
def plotly_table(df: pd.DataFrame):
    fig = go.Figure(
        data=[go.Table(
            header=dict(values=list(df.reset_index().columns), fill_color="#0078FF",
                        align="center", font=dict(color="white", size=13), height=30),
            cells=dict(values=[df.reset_index()[col] for col in df.reset_index().columns],
                       fill_color="#F9FBFD", align="center", height=25)
        )]
    )
    fig.update_layout(margin=dict(l=0, r=0, t=20, b=0))
    return fig

# -------------------------
# Placeholder functions
# -------------------------
def close_chart(data, period='1y'):
    fig = go.Figure()
    df = _slice_period(data, period)
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close'))
    fig.update_layout(title='Close Price', template='plotly_white', height=400)
    return fig

def Moving_average(data, period='1y'):
    df = _slice_period(data, period)
    df['MA7'] = df['Close'].rolling(7).mean()
    df['MA30'] = df['Close'].rolling(30).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close'))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA7'], mode='lines', name='7-day MA'))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA30'], mode='lines', name='30-day MA'))
    fig.update_layout(title='Moving Average', template='plotly_white', height=400)
    return fig

def MACD(data, period='1y'):
    df = _slice_period(data, period)
    macd = ta.trend.MACD(df['Close'])
    df['MACD'] = macd.macd()
    df['Signal'] = macd.macd_signal()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], mode='lines', name='MACD'))
    fig.add_trace(go.Scatter(x=df.index, y=df['Signal'], mode='lines', name='Signal'))
    fig.update_layout(title='MACD Indicator', template='plotly_white', height=300)
    return fig

def candlestick(data, period='1y'):
    df = _slice_period(data, period)
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close']
    )])
    fig.update_layout(title='Candlestick Chart', template='plotly_white', height=400)
    return fig

def Moving_average_forecast(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close Price'))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA7'] if 'MA7' in df else df['Close'],
                             mode='lines', name='7-day MA'))
    fig.update_layout(title='Stock Price Forecast', template='plotly_white', height=400)
    return fig
