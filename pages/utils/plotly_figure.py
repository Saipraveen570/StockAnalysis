import plotly.graph_objects as go
import datetime
import pandas as pd
import ta

def plotly_table(dataframe):
    headerColor = 'grey'
    rowEvenColor = '#f8fafd'
    rowOddColor = '#e1efff'
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=["<b>"]+["<b>"+str(i)[:10]+"<b>" for i in dataframe.columns],
            line_color='#0078ff', fill_color='#0078ff',
            align='center', font=dict(color='white', size=15), height=35,
        ),
        cells=dict(
            values=[["<b>"+str(i)+"<b>" for i in dataframe.index]] + [dataframe[i] for i in dataframe.columns],
            fill_color=[[rowOddColor,rowEvenColor]*10],
            align='left', line_color=['white'], font=dict(color=["black"], size=15)
        )
    )])
    fig.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0))
    return fig

def filter_data(dataframe, num_period):
    if num_period == '1mo':
        date = dataframe.index[-1] - pd.DateOffset(months=1)
    elif num_period == '5d':
        date = dataframe.index[-1] - pd.DateOffset(days=5)
    elif num_period == '6mo':
        date = dataframe.index[-1] - pd.DateOffset(months=6)
    elif num_period == '1y':
        date = dataframe.index[-1] - pd.DateOffset(years=1)
    elif num_period == '5y':
        date = dataframe.index[-1] - pd.DateOffset(years=5)
    elif num_period == 'ytd':
        date = pd.Timestamp(datetime.datetime(dataframe.index[-1].year,1,1))
    else:
        date = dataframe.index[0]
    return dataframe[dataframe.index > date]

def close_chart(dataframe, num_period=False):
    if num_period:
        dataframe = filter_data(dataframe, num_period)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dataframe.index, y=dataframe['Open'], mode='lines', name='Open', line=dict(width=2,color='#5ab7ff')))
    fig.add_trace(go.Scatter(x=dataframe.index, y=dataframe['Close'], mode='lines', name='Close', line=dict(width=2,color='black')))
    fig.add_trace(go.Scatter(x=dataframe.index, y=dataframe['High'], mode='lines', name='High', line=dict(width=2,color='#0078ff')))
    fig.add_trace(go.Scatter(x=dataframe.index, y=dataframe['Low'], mode='lines', name='Low', line=dict(width=2,color='red')))
    fig.update_xaxes(rangeslider_visible=True)
    fig.update_layout(height=500, margin=dict(l=0,r=20,t=20,b=0), plot_bgcolor='white', paper_bgcolor='#e1efff')
    return fig

def RSI(dataframe, num_period):
    df = dataframe.copy()
    df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
    df = filter_data(df, num_period)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(width=2,color='orange')))
    fig.add_trace(go.Scatter(x=df.index, y=[70]*len(df), name='Overbought', line=dict(width=2,color='red', dash='dash')))
    fig.add_trace(go.Scatter(x=df.index, y=[30]*len(df), name='Oversold', line=dict(width=2,color='#79da84', dash='dash')))
    fig.update_layout(height=200, plot_bgcolor='white', paper_bgcolor='#e1efff', margin=dict(l=0,r=0,t=0,b=0))
    return fig

def Moving_average(dataframe, num_period):
    df = dataframe.copy()
    df['SMA_50'] = ta.trend.SMAIndicator(df['Close'], window=50).sma_indicator()
    df = filter_data(df, num_period)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close', line=dict(width=2,color='black')))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], mode='lines', name='SMA 50', line=dict(width=2,color='purple')))
    fig.update_layout(height=500, margin=dict(l=0,r=20,t=20,b=0), plot_bgcolor='white', paper_bgcolor='#e1efff')
    return fig

def Moving_average_forecast(forecast):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=forecast.index[:-30], y=forecast['Close'].iloc[:-30], mode='lines', name='Close Price', line=dict(width=2,color='black')))
    fig.add_trace(go.Scatter(x=forecast.index[-31:], y=forecast['Close'].iloc[-31:], mode='lines', name='Future Close Price', line=dict(width=2,color='red')))
    fig.update_xaxes(rangeslider_visible=True)
    fig.update_layout(height=500, margin=dict(l=0,r=20,t=20,b=0), plot_bgcolor='white', paper_bgcolor='#e1efff')
    return fig
