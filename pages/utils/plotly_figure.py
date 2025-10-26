import plotly.graph_objects as go
import pandas as pd

# -------------------------------
# Simple Plotly table
# -------------------------------
def plotly_table(df):
    df = df.copy()
    if 'Value' not in df.columns:
        df['Value'] = df.iloc[:,0]
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns), fill_color='lightskyblue', align='left'),
        cells=dict(values=[df.index, df['Value']], fill_color='lavender', align='left')
    )])
    return fig

# -------------------------------
# Moving Average Forecast Chart
# -------------------------------
def Moving_average_forecast(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Close'], mode='lines', name='Close'
    ))
    if 'MA7' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['MA7'], mode='lines', name='MA7'
        ))
    fig.update_layout(title="📈 Close Price with 7-Day MA", xaxis_title="Date", yaxis_title="Price")
    return fig
