import plotly.graph_objects as go
import pandas as pd

# -------------------------------
# Function to create a Plotly Table
# -------------------------------
def plotly_table(df: pd.DataFrame):
    """
    Create a simple Plotly table from a DataFrame.
    Expects DataFrame with index and a single column named 'Value'.
    """
    fig = go.Figure(data=[go.Table(
        header=dict(values=['Metric', 'Value'],
                    fill_color='lightskyblue',
                    align='left'),
        cells=dict(values=[df.index, df['Value']],
                   fill_color='lavender',
                   align='left'))
    ])
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=10))
    return fig

# -------------------------------
# Function to create Moving Average Chart
# -------------------------------
def Moving_average_forecast(df: pd.DataFrame):
    """
    Create a line chart for Close price and Moving Average.
    Expects DataFrame with 'Close' and 'MA7' columns.
    """
    fig = go.Figure()
    
    # Plot Close Price
    if 'Close' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Close'],
            mode='lines',
            name='Close Price',
            line=dict(color='blue')
        ))

    # Plot Moving Average
    if 'MA7' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['MA7'],
            mode='lines',
            name='7-Day MA',
            line=dict(color='orange', dash='dot')
        ))

    fig.update_layout(
        title='💹 Price & Moving Average',
        xaxis_title='Date',
        yaxis_title='Price',
        template='plotly_white',
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig
