import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from model_train import get_data, train_model, save_model, load_model, forecast

st.set_page_config(page_title="Stock Prediction", page_icon="📈", layout="wide")

st.title("Stock Price Forecast 📈")
st.write("Predict future closing prices of stocks using SARIMAX model.")

# -----------------------------------------------------------
# Input
# -----------------------------------------------------------
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, TSLA, INFY.NS)", "AAPL")

if st.button("Run Forecast"):
    
    with st.spinner("Fetching data..."):
        df = get_data(ticker)

    if df.empty:
        st.error("Unable to fetch data. Please enter a valid ticker.")
        st.stop()

    st.success("✅ Data loaded successfully")

    model, scaler = load_model(ticker)

    # Train if no saved model exists
    if model is None or scaler is None:
        st.info("Training new model for this stock...")
        with st.spinner("Training SARIMAX model..."):
            model, scaler = train_model(df)

        if model is None:
            st.error("Model training failed. Try again later.")
            st.stop()

        save_model(model, scaler, ticker)
        st.success("✅ Model trained & saved")

    # Forecast
    with st.spinner("Generating forecast..."):
        future_pred = forecast(model, scaler, steps=30)

    if len(future_pred) == 0:
        st.error("Forecasting failed.")
        st.stop()

    st.success("✅ Forecast generated")

    # -----------------------------------------------------------
    # Plot
    # -----------------------------------------------------------
    last_date = df.index[-1]
    future_dates = pd.date_range(last_date, periods=30)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Historical"))
    fig.add_trace(go.Scatter(x=future_dates, y=future_pred, mode="lines", name="Forecast"))

    fig.update_layout(
        title=f"{ticker} Stock Price Forecast",
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------------------------------------
    # Display predicted numbers
    # -----------------------------------------------------------
    st.write("### Forecasted Prices (Next 30 Days)")
    forecast_df = pd.DataFrame({
        "Date": future_dates,
        "Predicted Close Price": np.round(future_pred, 2)
    })

    st.dataframe(forecast_df)
