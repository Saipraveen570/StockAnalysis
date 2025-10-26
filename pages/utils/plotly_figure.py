import plotly.graph_objects as go
import pandas as pd

# -------------------------------
# Plotly Table
# -------------------------------
def plotly_table(df: pd.DataFrame):
    """
    Create a Plotly Table from a DataFrame with columns 'Value' and index as metrics.
    Handles missing data gracefully.
    """
    df = df.copy()
    if 'Value' not in df.columns:
        df['Value'] = ['N/A'] * len(df)
    df = df.fillna('N/A')
    
    fig = go.Figure(
        data=[go.Table(
            header=dict(values=['Metric', 'Value'], fill_color='paleturquoise', align='left'),
            cells=dict(values=[df.index, df['Value']], fill_color='lavender', align='left')
        )]
    )
    fig.update_layout(margin=dict(l=0,r=0,t=0,b=0))
    return fig


# -------------------------------
# Closing Price Line Chart
# -------------------------------
def close_chart(df: pd.DataFrame, period: str):
    df_plot = df.copy()
    df_plot = df_plot.dropna(subset=['Close'])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['Close'], mode='lines', name='Close'))
    fig.update_layout(title="Closing Price", xaxis_title="Date", yaxis_title="Price ($)", template="plotly_white")
    return fig


# -------------------------------
# Candlestick Chart
# -------------------------------
def candlestick(df: pd.DataFrame, period: str):
    df_plot = df.copy()
    df_plot = df_plot.dropna(subset=['Open', 'High', 'Low', 'Close'])
    fig = go.Figure(
        data=[go.Candlestick(
            x=df_plot.index,
            open=df_plot['Open'],
            high=df_plot['High'],
            low=df_plot['Low'],
            close=df_plot['Close']
        )]
    )
    fig.update_layout(title="Candlestick Chart", xaxis_title="Date", yaxis_title="Price ($)", template="plotly_white")
    return fig


# -------------------------------
# Moving Average Chart
# -------------------------------
def Moving_average(df: pd.DataFrame, period: str, window: int = 7):
    df_plot = df.copy()
    df_plot = df_plot.dropna(subset=['Close'])
    df_plot['MA'] = df_plot['Close'].rolling(window).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['Close'], mode='lines', name='Close'))
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['MA'], mode='lines', name=f'{window}-day MA'))
    fig.update_layout(title=f"Moving Average ({window}-day)", xaxis_title="Date", yaxis_title="Price ($)", template="plotly_white")
    return fig


# -------------------------------
# RSI Chart
# -------------------------------
def RSI(df: pd.DataFrame, period: str, window: int = 14):
    df_plot = df.copy()
    df_plot = df_plot.dropna(subset=['Close'])
    delta = df_plot['Close'].diff()
    up = delta.clip(lower=0)
    down = -1*delta.clip(upper=0)
    roll_up = up.rolling(window).mean()
    roll_down = down.rolling(window).mean()
    rs = roll_up / (roll_down + 1e-6)
    rsi = 100 - (100 / (1 + rs))
    df_plot['RSI'] = rsi.fillna(0)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['RSI'], mode='lines', name='RSI'))
    fig.update_layout(title=f"RSI ({window}-day)", xaxis_title="Date", yaxis_title="RSI", template="plotly_white")
    fig.update_yaxes(range=[0,100])
    return fig


# -------------------------------
# MACD Chart
# -------------------------------
def MACD(df: pd.DataFrame, period: str):
    df_plot = df.copy()
    df_plot = df_plot.dropna(subset=['Close'])
    exp12 = df_plot['Close'].ewm(span=12, adjust=False).mean()
    exp26 = df_plot['Close'].ewm(span=26, adjust=False).mean()
    macd = exp12 - exp26
    signal = macd.ewm(span=9, adjust=False).mean()
    df_plot['MACD'] = macd
    df_plot['Signal'] = signal

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['MACD'], mode='lines', name='MACD'))
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['Signal'], mode='lines', name='Signal'))
    fig.update_layout(title="MACD", xaxis_title="Date", yaxis_title="MACD Value", template="plotly_white")
    return fig


# -------------------------------
# Forecast Moving Average Chart
# -------------------------------
def Moving_average_forecast(df: pd.DataFrame):
    df_plot = df.copy()
    df_plot = df_plot.dropna(subset=['Close'])
    df_plot['MA7'] = df_plot['Close'].rolling(7).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['Close'], mode='lines', name='Close'))
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['MA7'], mode='lines', name='7-day MA'))
    fig.update_layout(title="Forecast vs Moving Average", xaxis_title="Date", yaxis_title="Price ($)", template="plotly_white")
    return fig
