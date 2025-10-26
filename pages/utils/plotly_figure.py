import plotly.graph_objects as go
import pandas as pd

# -------------------------------
# Flexible Table
# -------------------------------
def plotly_table(df: pd.DataFrame):
    """
    Create a Plotly table from a DataFrame.
    Accepts any column names.
    """
    columns = df.columns.tolist()
    values = [df.index.tolist()] + [df[col].tolist() for col in columns]

    fig = go.Figure(
        data=[go.Table(
            header=dict(values=["Index"] + columns,
                        fill_color='paleturquoise',
                        align='left'),
            cells=dict(values=values,
                       fill_color='lavender',
                       align='left'))
        ]
    )
    return fig

# -------------------------------
# Close Price Line Chart
# -------------------------------
def close_chart(df, period='1y'):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Close'],
        mode='lines',
        name='Close Price'
    ))
    fig.update_layout(title=f'Close Price ({period})')
    return fig

# -------------------------------
# Candlestick Chart
# -------------------------------
def candlestick(df, period='1y'):
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close']
    )])
    fig.update_layout(title=f'Candlestick Chart ({period})')
    return fig

# -------------------------------
# RSI Indicator
# -------------------------------
def RSI(df, period='1y', window=14):
    import ta
    df_rsi = df.copy()
    df_rsi['RSI'] = ta.momentum.RSIIndicator(df_rsi['Close'], window=window).rsi()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_rsi.index, y=df_rsi['RSI'], mode='lines', name='RSI'))
    fig.update_layout(title=f'RSI ({window}-day) ({period})')
    return fig

# -------------------------------
# Moving Average
# -------------------------------
def Moving_average(df, period='1y', window=7):
    df_ma = df.copy()
    df_ma[f'MA{window}'] = df_ma['Close'].rolling(window).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_ma.index, y=df_ma['Close'], mode='lines', name='Close'))
    fig.add_trace(go.Scatter(x=df_ma.index, y=df_ma[f'MA{window}'], mode='lines', name=f'MA{window}'))
    fig.update_layout(title=f'Close Price with {window}-day MA ({period})')
    return fig

# -------------------------------
# MACD Indicator
# -------------------------------
def MACD(df, period='1y'):
    import ta
    df_macd = df.copy()
    macd_indicator = ta.trend.MACD(df_macd['Close'])
    df_macd['MACD'] = macd_indicator.macd()
    df_macd['Signal'] = macd_indicator.macd_signal()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_macd.index, y=df_macd['MACD'], mode='lines', name='MACD'))
    fig.add_trace(go.Scatter(x=df_macd.index, y=df_macd['Signal'], mode='lines', name='Signal'))
    fig.update_layout(title=f'MACD ({period})')
    return fig

# -------------------------------
# Moving Average Forecast Chart
# -------------------------------
def Moving_average_forecast(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close'))
    if 'MA7' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['MA7'], mode='lines', name='MA7'))
    fig.update_layout(title='Close Price Forecast with Moving Average')
    return fig
