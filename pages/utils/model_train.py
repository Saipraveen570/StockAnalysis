import yfinance as yf
import pandas as pd
import numpy as np
import time
from sklearn.preprocessing import MinMaxScaler
from statsmodels.tsa.statespace.sarimax import SARIMAX
from pmdarima import auto_arima
import joblib
import streamlit as st

# -----------------------------------------------------------
# ✅ Fetch Stock Data (Cached)
# -----------------------------------------------------------
@st.cache_data(show_spinner=True)
def get_data(ticker):
    retries = 5
    for _ in range(retries):
        try:
            df = yf.download(ticker, period="5y", progress=False, threads=False)
            if not df.empty:
                df.dropna(inplace=True)
                return df
        except:
            time.sleep(1)
    return pd.DataFrame()

# -----------------------------------------------------------
# ✅ Feature Engineering - Log Returns
# -----------------------------------------------------------
def prepare_data(df):
    df["Log_Returns"] = np.log(df["Close"] / df["Close"].shift(1))
    df.dropna(inplace=True)
    return df

# -----------------------------------------------------------
# ✅ Scaling Helpers
# -----------------------------------------------------------
def scale_data(series):
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(series.values.reshape(-1, 1))
    return scaled, scaler

def inverse_scale(scaled, scaler):
    return scaler.inverse_transform(scaled)

# -----------------------------------------------------------
# ✅ Train SARIMAX Model (Auto-Tuned)
# -----------------------------------------------------------
def train_model(df):
    if df.empty or "Close" not in df.columns:
        return None, None

    df = prepare_data(df)
    returns = df["Log_Returns"]

    scaled_data, scaler = scale_data(returns)

    # Automatically determine best SARIMA configuration
    with st.spinner("🔍 Auto-tuning SARIMAX parameters..."):
        try:
            auto_model = auto_arima(
                scaled_data,
                seasonal=True,
                m=12,
                stepwise=True,
                suppress_warnings=True,
                max_p=3, max_q=3, max_P=2, max_Q=2
            )
            order = auto_model.order
            seasonal_order = auto_model.seasonal_order
        except Exception as e:
            st.warning(f"Auto-ARIMA tuning failed: {e}")
            order, seasonal_order = (1, 1, 1), (1, 1, 1, 12)

    # Fit final SARIMAX model
    model = SARIMAX(
        scaled_data,
        order=order,
        seasonal_order=seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False
    )

    results = model.fit(disp=False)
    return results, scaler

# -----------------------------------------------------------
# ✅ Save & Load Model
# -----------------------------------------------------------
def save_model(model, scaler, ticker):
    joblib.dump(model, f"{ticker}_model.pkl")
    joblib.dump(scaler, f"{ticker}_scaler.pkl")

def load_model(ticker):
    try:
        model = joblib.load(f"{ticker}_model.pkl")
        scaler = joblib.load(f"{ticker}_scaler.pkl")
        return model, scaler
    except:
        return None, None

# -----------------------------------------------------------
# ✅ Forecast Future Prices
# -----------------------------------------------------------
def forecast(model, scaler, df, steps=30):
    try:
        # Forecast future log returns
        pred_scaled = model.forecast(steps=steps)
        pred_returns = inverse_scale(pred_scaled.reshape(-1, 1), scaler).flatten()

        # Convert log returns → cumulative price forecast
        last_close = df["Close"].iloc[-1]
        forecast_prices = [last_close]

        for r in pred_returns:
            next_price = forecast_prices[-1] * np.exp(r)
            forecast_prices.append(next_price)

        return forecast_prices[1:]
    except Exception as e:
        st.error(f"Forecasting failed: {e}")
        return []

# -----------------------------------------------------------
# ✅ Example Streamlit usage
# -----------------------------------------------------------
if __name__ == "__main__":
    st.title("📈 Stock Forecast Trainer (SARIMAX Enhanced)")

    ticker = st.text_input("Enter Stock Symbol (e.g. AAPL, INFY.NS):", "AAPL")
    if ticker:
        df = get_data(ticker)

        if not df.empty:
            st.success(f"✅ Loaded {len(df)} rows for {ticker}")

            model, scaler = train_model(df)
            if model:
                st.success("✅ Model trained successfully!")

                future_prices = forecast(model, scaler, df, steps=30)
                st.line_chart(future_prices)
            else:
                st.error("❌ Model training failed.")
        else:
            st.error("❌ Failed to load stock data.")
