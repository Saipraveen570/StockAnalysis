import plotly.graph_objects as go
import pandas as pd

# -------------------------
# Table for metrics / historical data
# -------------------------
def plotly_table(df: pd.DataFrame) -> go.Figure:
    if 'Value' not in df.columns:
        df['Value'] = df.iloc[:, 0]
    fig = go.Figure(data=[go.Table(
        header=dict(values=["Metric", "Value"], fill_color='paleturquoise', align='left'),
        cells=dict(values=[df.index, df['Value']], fill_color='lavender', align='left')
    )])
    fig.update_layout(margin=dict(l=5,r=5,t=5,b=5))
    return fig

# -------------------------
# Line chart for closing price
# -------------------------
def close_chart(df: pd.DataFrame, period: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close'))
    fig.update_layout(title=f"Close Price ({period})", xaxis_title="Date", yaxis_title="Price")
    return fig

# -------------------------
# Candlestick chart
# -------------------------
def candlestick(df: pd.DataFrame, period: str) -> go.Figure:
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close']
    )])
    fig.update_layout(title=f"Candlestick Chart ({period})", xaxis_title="Date", yaxis_title="Price")
    return fig

# -------------------------
# RSI indicator
# -------------------------
def RSI(df: pd.DataFrame, period: str, window: int = 14) -> go.Figure:
    delta = df['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=rsi, mode='lines', name=f'RSI {window}'))
    fig.update_layout(title=f"RSI ({window}-day)", xaxis_title="Date", yaxis_title="RSI")
    return fig

# -------------------------
# Moving Average
# -------------------------
def Moving_average(df: pd.DataFrame, period: str, window: int = 20) -> go.Figure:
    ma = df['Close'].rolling(window=window).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close'))
    fig.add_trace(go.Scatter(x=df.index, y=ma, mode='lines', name=f'MA {window}'))
    fig.update_layout(title=f"Moving Average ({window}-day)", xaxis_title="Date", yaxis_title="Price")
    return fig

# -------------------------
# MACD indicator
# -------------------------
def MACD(df: pd.DataFrame, period: str, fast: int = 12, slow: int = 26, signal: int = 9) -> go.Figure:
    ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=macd_line, mode='lines', name='MACD'))
    fig.add_trace(go.Scatter(x=df.index, y=signal_line, mode='lines', name='Signal'))
    fig.update_layout(title=f"MACD ({fast},{slow},{signal})", xaxis_title="Date", yaxis_title="Value")
    return fig

# -------------------------
# Moving Average Forecast for predictions
# -------------------------
def Moving_average_forecast(df: pd.DataFrame, window: int = 7) -> go.Figure:
    df_ma = df.copy()
    df_ma['MA'] = df_ma['Close'].rolling(window=window).mean()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_ma.index, y=df_ma['Close'], mode='lines', name='Close'))
    fig.add_trace(go.Scatter(x=df_ma.index, y=df_ma['MA'], mode='lines', name=f'{window}-day MA'))
    
    fig.update_layout(title=f"Moving Average Forecast ({window}-day)", xaxis_title="Date", yaxis_title="Price")
    return fig
