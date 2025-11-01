import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ------------------ 1️⃣ CANDLESTICK CHART ------------------
def candlestick(data: pd.DataFrame):
    """Create a candlestick chart."""
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name='Price'
            )
        ]
    )
    fig.update_layout(
        title="📊 Candlestick Chart",
        yaxis_title="Price (USD)",
        xaxis_title="Date",
        template="plotly_dark",
        height=500
    )
    return fig

# ------------------ 2️⃣ RELATIVE STRENGTH INDEX (RSI) ------------------
def RSI(data: pd.DataFrame, period: int = 14):
    """Compute and plot the Relative Strength Index."""
    delta = data['Close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=period).mean()
    avg_loss = pd.Series(loss).rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=rsi, mode='lines', name='RSI', line=dict(color='cyan')))
    fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
    fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")
    fig.update_layout(title="💪 RSI Indicator", yaxis_title="RSI", template="plotly_dark", height=400)
    return fig

# ------------------ 3️⃣ MOVING AVERAGES ------------------
def Moving_average(data: pd.DataFrame, short_window: int = 20, long_window: int = 50):
    """Plot short-term and long-term moving averages."""
    data['MA_Short'] = data['Close'].rolling(window=short_window).mean()
    data['MA_Long'] = data['Close'].rolling(window=long_window).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close Price', line=dict(color='lightgray')))
    fig.add_trace(go.Scatter(x=data.index, y=data['MA_Short'], mode='lines', name=f'{short_window}-Day MA', line=dict(color='yellow')))
    fig.add_trace(go.Scatter(x=data.index, y=data['MA_Long'], mode='lines', name=f'{long_window}-Day MA', line=dict(color='orange')))
    fig.update_layout(title="📈 Moving Average Chart", yaxis_title="Price (USD)", template="plotly_dark", height=450)
    return fig

# ------------------ 4️⃣ MACD (Moving Average Convergence Divergence) ------------------
def MACD(data: pd.DataFrame, short_window: int = 12, long_window: int = 26, signal_window: int = 9):
    """Plot MACD line, signal line, and histogram."""
    exp1 = data['Close'].ewm(span=short_window, adjust=False).mean()
    exp2 = data['Close'].ewm(span=long_window, adjust=False).mean()
    macd_line = exp1 - exp2
    signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
    hist = macd_line - signal_line

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=macd_line, mode='lines', name='MACD Line', line=dict(color='cyan')))
    fig.add_trace(go.Scatter(x=data.index, y=signal_line, mode='lines', name='Signal Line', line=dict(color='orange')))
    fig.add_trace(go.Bar(x=data.index, y=hist, name='Histogram', marker_color='gray'))
    fig.update_layout(title="📊 MACD Indicator", yaxis_title="MACD", template="plotly_dark", height=450)
    return fig
