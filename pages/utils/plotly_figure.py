import plotly.graph_objects as go
import dateutil
import ta
import datetime
import pandas as pd

def plotly_table(dataframe):
    headerColor = 'grey'
    rowEvenColor = '#f8fafd'
    rowOddColor = '#e1efff'

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=["<b>Date</b>"] + [f"<b>{col}</b>" for col in dataframe.columns],
            line_color='#0078ff', fill_color='#0078ff',
            align='center', font=dict(color='white', size=15), height=35,
        ),
        cells=dict(
            values=[[str(idx) for idx in dataframe.index]] + [dataframe[col].tolist() for col in dataframe.columns],
            fill_color=[[rowOddColor, rowEvenColor] * (len(dataframe)//2 + 1)],
            align='left', line_color=['white'], font=dict(color="black", size=14)
        )
    )])
    fig.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0))
    return fig


def filter_data(dataframe, num_period):
    if dataframe.empty:
        return dataframe

    df = dataframe.copy()

    try:
        last_date = df.index[-1]
    except:
        return df

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
        date = df.index[0]

    df = df.reset_index()
    df = df[df['Date'] > date]
    return df


def safe_get(df, col):
    return df[col] if col in df.columns else pd.Series([None]*len(df))


def close_chart(dataframe, num_period=False):
    df = dataframe.copy()
    if num_period:
        df = filter_data(df, num_period)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=safe_get(df, 'Open'), mode='lines', name='Open'))
    fig.add_trace(go.Scatter(x=df['Date'], y=safe_get(df, 'Close'), mode='lines', name='Close'))
    fig.add_trace(go.Scatter(x=df['Date'], y=safe_get(df, 'High'), mode='lines', name='High'))
    fig.add_trace(go.Scatter(x=df['Date'], y=safe_get(df, 'Low'), mode='lines', name='Low'))

    fig.update_xaxes(rangeslider_visible=True)
    fig.update_layout(height=500, margin=dict(l=0, r=20, t=20, b=0))
    return fig


def candlestick(dataframe, num_period):
    df = filter_data(dataframe.copy(), num_period)

    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df['Date'], open=safe_get(df, 'Open'),
        high=safe_get(df, 'High'), low=safe_get(df, 'Low'),
        close=safe_get(df, 'Close')
    ))
    fig.update_layout(showlegend=False, height=500, margin=dict(l=0, r=20, t=20, b=0))
    return fig


def RSI(dataframe, num_period):
    df = dataframe.copy()
    df["RSI"] = ta.momentum.RSIIndicator(df["Close"]).rsi()
    df = filter_data(df, num_period)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['RSI'], name='RSI'))
    fig.add_trace(go.Scatter(x=df['Date'], y=[70]*len(df), name='Overbought', line=dict(dash='dash')))
    fig.add_trace(go.Scatter(x=df['Date'], y=[30]*len(df), name='Oversold', line=dict(dash='dash')))
    fig.update_layout(yaxis_range=[0, 100], height=200, margin=dict(l=0, r=0, t=0, b=0))
    return fig


def Moving_average(dataframe, num_period):
    df = dataframe.copy()
    df['SMA_50'] = ta.trend.SMAIndicator(df['Close'], 50).sma_indicator()
    df = filter_data(df, num_period)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=safe_get(df, 'Close'), name='Close'))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA_50'], name='SMA 50'))
    fig.update_xaxes(rangeslider_visible=True)
    fig.update_layout(height=500, margin=dict(l=0, r=20, t=20, b=0))
    return fig


def MACD(dataframe, num_period):
    df = dataframe.copy()
    macd_calc = ta.trend.MACD(df['Close'])

    df['MACD'] = macd_calc.macd()
    df['MACD Signal'] = macd_calc.macd_signal()
    df['MACD Hist'] = macd_calc.macd_diff()

    df = filter_data(df, num_period)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['MACD'], name='MACD'))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['MACD Signal'], name='Signal', line=dict(dash='dash')))
    fig.add_trace(go.Bar(x=df['Date'], y=df['MACD Hist'], name='Histogram'))

    fig.update_layout(height=200, margin=dict(l=0, r=0, t=0, b=0))
    return fig
