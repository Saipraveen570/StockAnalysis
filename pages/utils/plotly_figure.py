import plotly.graph_objects as go
import pandas as pd

# -------------------------------
# Table for Streamlit
# -------------------------------
def plotly_table(df: pd.DataFrame):
    """
    Creates a Plotly table from a DataFrame.
    Ensures 'Value' column exists to prevent KeyErrors.
    """
    if 'Value' not in df.columns:
        df['Value'] = df.iloc[:, 0]  # fallback: take first column as Value

    fig = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns),
                    fill_color='lightblue',
                    align='left'),
        cells=dict(values=[df.index, df['Value']],
                   fill_color='lavender',
                   align='left'))
    ])
    return fig

# -------------------------------
# Moving Average + Forecast Chart
# -------------------------------
def Moving_average_forecast(df: pd.DataFrame):
    """
    Plots combined Close price and 7-day moving average.
    """
    fig = go.Figure()
    if 'Close' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Close'],
            mode='lines+markers',
            name='Close Price',
            line=dict(color='blue')
        ))

    if 'MA7' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['MA7'],
            mode='lines',
            name='7-Day MA',
            line=dict(color='orange', dash='dash')
        ))

    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Price',
        template='plotly_white',
        margin=dict(l=40, r=40, t=60, b=40)
    )

    return fig
