import plotly.graph_objects as go
import dateutil
import datetime
import pandas as pd

# Try importing `ta`; avoid crash if missing
try:
    import ta
except ImportError:
    ta = None


def plotly_table(dataframe):
    headerColor = "#0078ff"
    rowEvenColor = "#f8fafd"
    rowOddColor = "#e1efff"

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=["<b>Date</b>"] + [f"<b>{col}</b>" for col in dataframe.columns],
            line_color=headerColor, fill_color=headerColor,
            align='center', font=dict(color='white', size=14), height=35,
        ),
        cells=dict(
            values=[[str(idx) for idx in dataframe.index]] + [dataframe[col].tolist() for col in dataframe.columns],
            fill_color=[[rowOddColor, rowEvenColor] * (len(dataframe) // 2 + 1)],
            align='left', font=dict(color="black", size=13)
        )
    )])

    fig.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0))
    return fig


def filter_data(df, num_period):
    if df.empty:
        return df

    last_date = df.index[-1]

    if num_period == '1mo':
        date = last_date + dateutil.relativedelta.relativedelta(months=-1)
    elif num_period == '5d':
        date = last_date + dateutil.relativedelta.relativedelta(days=-5)
    elif num_period == '6mo':
        date = last_date + dateutil.relativedelta.relativedelta(months=-6)
    elif num_period == '1y':
        date = last_date + dateutil.relativedelta.relativedelta(years=-1)
    elif num_period == '5y':
        date = last_date + dateutil.relativedelta.relativedelta(years=-5)
    elif num_period == 'ytd':
        date = datetime.datetime(last_date.year, 1, 1)
    else:
        return df

    df = df.reset_index()
    return df[df['Date'] > date]


def safe_get(df, col):
    return df[col] if col in df.columns else pd.Series([None]*len(df))


def close_chart(df, num_period=None):
    if num_period:
        df = filter_data(df.copy(), num_period)

    fig = go.Figure()
    for col in ['Open', 'Close', 'High', 'Low']:
        fig.add_trace(go.Scatter(x=df['Date'], y=safe_get(df, col), mode='lines', name=col))

    fig.update_layout(height=450, margin=dict(l=0, r=20, t=20, b=0))
    return fig


def candlestick(df, num_period=None):
    if num_period:
        df = filter_data(df.copy(), num_period)

    fig = go.Figure(go.Candlestick(
        x=df['Date'], open=safe_get(df, 'Open'),
        high=safe_get(df, 'High'), low=safe_get(df, 'Low'),
        close=safe_get(df, 'Close')
    ))

    fig.update_layout(showlegend=False, height=450, margin=dict(l=0, r=20, t=20, b=0))
    return fig


def RSI(df, num_period=None):
    if ta is None:
        return go.Figure()

    df = df.copy()
    df["RSI"] = ta.momentum.RSIIndicator(df["Close"]).rsi()

    if num_period:
        df = filter_data(df, num_period)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['RSI'], name='RSI'))
    fig.add_trace(go.Scatter(x=df['Date'], y=[70]*len(df), name='Overbought', line=dict(dash='dash')))
    fig.add_trace(go.Scatter(x=df['Date'], y=[30]*len(df), name='Oversold', line=dict(dash='dash')))

    fig.update_layout(yaxis_range=[0, 100], height=200, margin=dict(l=0, r=0, t=0, b=0))
    return fig


def Moving_average(df, num_period=None):
    df = df.copy()

    if ta:
        df['SMA_50'] = ta.trend.SMAIndicator(df['Close'], 50).sma_indicator()
    else:
        df['SMA_50'] = df['Close'].rolling(window=50).mean()

    if num_period:
        df = filter_data(df, num_period)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Close'))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], name='SMA 50'))

    fig.update_layout(height=450, margin=dict(l=0, r=20, t=20, b=0))
    return fig
