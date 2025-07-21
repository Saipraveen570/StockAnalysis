import plotly.graph_objs as go

def plot_forecast(data, forecast):
    fig = go.Figure()

    # Historical data
    fig.add_trace(go.Scatter(
        x=data.index, y=data['Close'],
        mode='lines',
        name='Historical',
        line=dict(color='blue')
    ))

    # Forecast data
    fig.add_trace(go.Scatter(
        x=forecast.index, y=forecast['Close'],
        mode='lines',
        name='Forecast (Next 30 Days)',
        line=dict(color='orange', dash='dash')
    ))

    fig.update_layout(
        title='Stock Price Forecast',
        xaxis_title='Date',
        yaxis_title='Close Price',
        template='plotly_white',
        legend=dict(x=0, y=1.1, orientation='h')
    )

    return fig
