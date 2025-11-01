import streamlit as st
import pandas as pd
from pages.utils.model_train import (
    get_data, train_model, load_model, save_model, forecast
)
from pages.utils.plotly_figure import plotly_table, Moving_average_forecast

st.set_page_config(
    page_title="Stock Prediction",
    page_icon="📉",
    layout="wide",
)

st.title("Stock Prediction")

ticker = st.text_input('Stock Ticker', 'AAPL').upper()

st.subheader(f"Predicting Next 30 Days Close Price for: {ticker}")

# Load or train model
data = get_data(ticker)

if data.empty:
    st.stop()

model, scaler = load_model(ticker)

if model is None:
    with st.spinner("Training model... Please wait."):
        model, scaler = train_model(data)
        save_model(model, scaler, ticker)

pred = forecast(model, scaler, steps=30)
future_dates = pd.date_range(start=data.index[-1], periods=30)

forecast_df = pd.DataFrame({"Date": future_dates, "Close": pred})
forecast_df.set_index("Date", inplace=True)

st.write("##### Forecast Data (Next 30 Days)")
fig = plotly_table(forecast_df.round(3))
fig.update_layout(height=220)
st.plotly_chart(fig, use_container_width=True)

combined = pd.concat([data["Close"], forecast_df])
st.plotly_chart(Moving_average_forecast(combined.tail(150)), use_container_width=True)
