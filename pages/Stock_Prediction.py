import streamlit as st
import pandas as pd
from pages.utils.model_train import get_data, get_rolling_mean, get_differencing_order, scaling, evaluate_model, get_forecast, inverse_scaling
from pages.utils.plotly_figure import plotly_table, Moving_average_forecast

# Page config
st.set_page_config(
    page_title="Stock Prediction",
    page_icon="chart_with_downwards_trend",
    layout="wide",
)

st.title("Stock Prediction")

col1, col2, col3 = st.columns(3)
with col1:
    ticker = st.text_input('Stock Ticker', 'AAPL')

st.subheader(f'Predicting Next 30 Days Close Price for: {ticker}')

# Fetch and preprocess data
close_price = get_data(ticker)
rolling_price = get_rolling_mean(close_price)

differencing_order = get_differencing_order(rolling_price)
scaled_data, scaler = scaling(rolling_price)

rmse = evaluate_model(scaled_data, differencing_order)
st.write("**Model RMSE Score:**", round(rmse, 4))

# Forecast
forecast = get_forecast(scaled_data, differencing_order)
forecast['Close'] = inverse_scaling(scaler, forecast['Close'])

st.write('##### Forecast Data (Next 30 Days)')
st.plotly_chart(plotly_table(forecast.sort_index().round(3)), use_container_width=True)

# Combined chart
combined = pd.concat([rolling_price, forecast])
st.plotly_chart(Moving_average_forecast(combined.iloc[150:]), use_container_width=True)
