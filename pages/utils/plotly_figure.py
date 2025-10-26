import plotly.graph_objects as go
import pandas_ta as pta
import pandas as pd
from datetime import datetime
import dateutil.relativedelta

# -------------------------
# Table
# -------------------------
def plotly_table(df):
    df = df.copy()
    header_color = '#0078ff'
    row_even = '#f8fafd'
    row_odd = '#e1efff'

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=["<b>Index</b>"] + [f"<b>{c}</b>" for c in df.columns],
            fill_color=header_color,
            line_color='white',
            align='center',
            font=dict(color='white', size=15),
            height=35
        ),
        cells=dict(
            values=[df.index] + [df[c].round(3) if pd.api.types.is_numeric_dtype(df[c]) else df[c] for c in df.columns],
            fill_color=[ [row_odd, row_even] * (len(df)//2 + 1) ],
            align='left',
            line_color='white',
            font=dict(color='black', size=15)
        )
    )])
    fig.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0))
    return fig

# -------------------------
# Filter data by period
# -------------------------
def filter_data(df, period):
    last_date = df.index[-1]
    if period == '1mo':
        start = last_date - dateutil.relativedelta.relativedelta(months=1)
    elif period == '5d':
        start = last_date - dateutil.relativedelta.relativedelta(days=5)
    elif period == '6mo':
        start = last_date - dateutil.relativedelta.relativedelta(months=6)
    elif period == '1y':
        start = last_date - dateutil.relativedelta.relativedelta(years=1)
    elif period == '5y':
        start = last_date - dateutil.relativedelta.relativedelta(years=5)
    elif period == 'ytd':
        start = datetime(last_date.year, 1, 1)
    else:
        start = df.index[0]
    return df[df.index >= start]

# -------------------------
# Close Price Chart
# -------------------------
def close_chart(df, period=None):
    data = filter_data(df, period) if period else df
    fig = go.Figure()
    for col, color in zip(['Open','Close','High','Low'], ['#5ab7ff','black','#0078ff','red']):
        if col in data.columns:
            fig.add_trace(go.Scatter(x=data.index, y=data[col], mode='lines', name=col, line=dict(width=2,color=color)))
    fig.update_xaxes(rangeslider_visible=True)
    fig.update_layout(height=500, margin=dict(l=0,r=20,t=20,b=0), plot_bgcolor='white', paper_bgcolor='#e1efff')
    return fig

# -------------------------
# Candlestick
# -------------------------
def candlestick(df, period=None):
    data = filter_data(df, period) if period else df
    fig = go.Figure(data=[go.Candlestick(x=data.index,
                                         open=data['Open'], high=data['High'],
                                         low=data['Low'], close=data['Close'])])
    fig.update_layout(height=500, margin=dict(l=0,r=20,t=20,b=0), plot_bgcolor='white', paper_bgcolor='#e1efff')
    return fig

# -------------------------
# RSI
# -------------------------
def RSI(df, period=None):
    df['RSI'] = pta.rsi(df['Close'])
    data = filter_data(df, period) if period else df
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], name='RSI', line=dict(width=2,color='orange')))
    fig.add_trace(go.Scatter(x=data.index, y=[70]*len(data), name='Overbought', line=dict(width=2,color='red',dash='dash')))
    fig.add_trace(go.Scatter(x=data.index, y=[30]*len(data), name='Oversold', line=dict(width=2,color='#79da84',dash='dash')))
    fig.update_layout(height=200, plot_bgcolor='white', paper_bgcolor='#e1efff', yaxis_range=[0,100])
    return fig

# -------------------------
# Moving Average Line
# -------------------------
def Moving_average(df, period=None, window=50):
    df['SMA_50'] = pta.sma(df['Close'], length=window)
    data = filter_data(df, period) if period else df
    fig = go.Figure()
    for col, color in zip(['Open','Close','High','Low'], ['#5ab7ff','black','#0078ff','red']):
        if col in data.columns:
            fig.add_trace(go.Scatter(x=data.index, y=data[col], mode='lines', name=col, line=dict(width=2,color=color)))
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA_50'], mode='lines', name=f'SMA {window}', line=dict(width=2,color='purple')))
    fig.update_xaxes(rangeslider_visible=True)
    fig.update_layout(height=500, margin=dict(l=0,r=20,t=20,b=0), plot_bgcolor='white', paper_bgcolor='#e1efff')
    return fig

# -------------------------
# Moving Average Forecast (Stock Prediction)
# -------------------------
def Moving_average_forecast(forecast):
    fig = go.Figure()
    n = len(forecast)
    split = min(30, n)
    fig.add_trace(go.Scatter(x=forecast.index[:-split], y=forecast['Close'].iloc[:-split], mode='lines', name='Close Price', line=dict(width=2,color='black')))
    fig.add_trace(go.Scatter(x=forecast.index[-split:], y=forecast['Close'].iloc[-split:], mode='lines', name='Future Close Price', line=dict(width=2,color='red')))
    fig.update_xaxes(rangeslider_visible=True)
    fig.update_layout(height=500, margin=dict(l=0,r=20,t=20,b=0), plot_bgcolor='white', paper_bgcolor='#e1efff')
    return fig
