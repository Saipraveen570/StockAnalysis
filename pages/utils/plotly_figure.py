import plotly.graph_objects as go
import pandas as pd
import ta

def plotly_table(df: pd.DataFrame) -> go.Figure:
    if 'Value' not in df.columns:
        df['Value'] = df[df.columns[0]]
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[df.index, df['Value']],
                   fill_color='lavender',
                   align='left'))
    ])
    return fig

def close_chart(df: pd.DataFrame, period: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close'))
    fig.update_layout(title=f"Close Price ({period})", xaxis_title="Date", yaxis_title="Price")
    return fig

def candlestick(df: pd.DataFrame, period: str) -> go.Figure:
    fig = go.Figure(data=[go.Candlestick(x=df.index,
                                         open=df['Open'],
                                         high=df['High'],
                                         low=df['Low'],
                                         close=df['Close'])])
    fig.update_layout(title=f"Candlestick Chart ({period})", xaxis_title="Date", yaxis_title="Price")
    return fig

def RSI(df: pd.DataFrame, period: str, window: int = 14) -> go.Figure:
    df_rsi = df.copy()
    df_rsi['RSI'] = ta.momentum.RSIIndicator(df_rsi['Close'], window=window).rsi()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_rsi.index, y=df_rsi['RSI'], mode='lines', name=f'RSI {window}'))
    fig.update_layout(title=f"RSI ({window}-day) ({period})", xaxis_title="Date", yaxis_title="RSI")
    return fig

def Moving_average(df: pd.DataFrame, period: str, window: int = 7) -> go.Figure:
    df_ma = df.copy()
    df_ma['MA'] = df_ma['Close'].rolling(window=window).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_ma.index, y=df_ma['Close'], mode='lines', name='Close'))
    fig.add_trace(go.Scatter(x=df_ma.index, y=df_ma['MA'], mode='lines', name=f'MA {window}'))
    fig.update_layout(title=f"Moving Average ({window}-day) ({period})", xaxis_title="Date", yaxis_title="Price")
    return fig

def MACD(df: pd.DataFrame, period: str, fast: int = 12, slow: int = 26, signal: int = 9) -> go.Figure:
    df_macd = df.copy()
    df_macd['EMA_fast'] = df_macd['Close'].ewm(span=fast, adjust=False).mean()
    df_macd['EMA_slow'] = df_macd['Close'].ewm(span=slow, adjust=False).mean()
    df_macd['MACD'] = df_macd['EMA_fast'] - df_macd['EMA_slow']
    df_macd['Signal'] = df_macd['MACD'].ewm(span=signal, adjust=False).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_macd.index, y=df_macd['MACD'], mode='lines', name='MACD'))
    fig.add_trace(go.Scatter(x=df_macd.index, y=df_macd['Signal'], mode='lines', name='Signal'))
    fig.update_layout(title=f"MACD ({fast},{slow},{signal}) ({period})", xaxis_title="Date", yaxis_title="MACD")
    return fig
