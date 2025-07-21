import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pages.utils.model_train import (
    get_data, 
    get_rolling_mean, 
    get_differencing_order, 
    scaling, 
    evaluate_model, 
    inverse_scaling
)
from statsmodels.tsa.statespace.sarimax import SARIMAX
from pages.utils.plotly_figure import plotly_table
import plotly.graph_objs as go

st.set_page_config(
    page_title="Stock Prediction",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Stock Prediction")

# ------------------- INPUT -------------------
col1, _, _ = st.columns(3)
with col1:
    ticker = st.text_input('Stock Ticker', 'AAPL')

st.subheader(f"Predicting Next 30 Days Close Price for: {ticker}")

# ------------------- DATA LOADING -------------------
close_price = get_data(ticker)
if close_price is None or close_price.empty:
    st.error("Failed to fetch data. Please check the stock ticker.")
    st.stop()

rolling_price = get_rolling_mean(close_price)
if rolling_price.isnull().sum() > 0:
    rolling_price = rolling_price.dropna()

differencing_order = get_differencing_order(rolling_price)
scaled_data, scaler = scaling(rolling_price)

# ------------------- MODEL EVALUATION -------------------
rmse = evaluate_model(scaled_data, differencing_order)
st.write("**Model RMSE Score:**", round(rmse, 4))

# ------------------- FORECAST FUNCTION -------------------
def get_forecast(series, d):
    try:
        model = SARIMAX(series, order=(1, d, 1), enforce_stationarity=False, enforce_invertibility=False)
        results = model.fit(disp=False)
        preds = results.forecast(steps=30)

        future_dates = pd.date_range(start=datetime.today(), periods=30, freq='D')
        forecast_df = pd.DataFrame(preds, index=future_dates, columns=['Close'])

        if forecast_df.isnull().values.any():
            st.warning("Forecast returned null values.")
            return pd.DataFrame()

        return forecast_df
    except Exception as e:
        st.error(f"Model training failed: {e}")
        return pd.DataFrame()

# ------------------- GET FORECAST -------------------
forecast_df = get_forecast(scaled_data, differencing_order)
if forecast_df.empty:
    st.stop()

# ------------------- INVERSE SCALING -------------------
forecast_df['Close'] = inverse_scaling(scaler, forecast_df['Close'])

# ------------------- DISPLAY TABLE -------------------
st.write("##### Forecast Data (Next 30 Days)")
st.dataframe(forecast_df.round(3))

# ------------------- PLOTLY CHART -------------------
def plot_forecast(forecast_df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=forecast_df.index, y=forecast_df['Close'], mode='lines+markers', name='Forecast'))
    fig.update_layout(
        title="📊 30-Day Stock Price Forecast",
        xaxis_title="Date",
        yaxis_title="Predicted Close Price",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

plot_forecast(forecast_df)

# ------------------- COMBINED WITH HISTORICAL -------------------
combined = pd.concat([rolling_price, forecast_df])
combined = combined[-180:]  # limit to last 6 months for clarity

fig = go.Figure()
fig.add_trace(go.Scatter(x=combined.index, y=combined['Close'], name='Actual & Forecast'))
fig.update_layout(title="📉 Historical + Forecast Trend", height=400)
st.plotly_chart(fig, use_container_width=True)
