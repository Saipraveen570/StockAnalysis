import yfinance as yf
import numpy as np
import pandas as pd
import time
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.preprocessing import MinMaxScaler
import joblib
import streamlit as st

# -----------------------------------------------------------
# Fetch Stock Data (Cached)
# -----------------------------------------------------------
@st.cache_data(show_spinner=True)
def get_data(ticker):
    retries = 5
    for _ in range(retries):
        try:
            df = yf.download(ticker, period="5y", progress=False, threads=False)
            if not df.empty:
                return df
        except:
            time.sleep(1)
    return pd.DataFrame()

# -----------------------------------------------------------
# Scaling Functions
# -----------------------------------------------------------
def scale_data(series):
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(series.values.reshape(-1, 1))
    return scaled, scaler

def inverse_scale(scaled, scaler):
    return scaler.inverse_transform(scaled)

# -----------------------------------------------------------
# Train SARIMAX Model
# -----------------------------------------------------------
def train_model(df):
    if df.empty or "Close" not in df.columns:
        return None, None

    close_prices = df["Close"]
    scaled_data, scaler = scale_data(close_prices)

    # Model configuration
    model = SARIMAX(
        scaled_data,
        order=(1, 1, 1),
        seasonal_order=(1, 1, 1, 12),
        enforce_stationarity=False,
        enforce_invertibility=False
    )

    results = model.fit(disp=False)
    return results, scaler

# -----------------------------------------------------------
# Save & Load Model
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
# Forecast Future Prices
# -----------------------------------------------------------
def forecast(model, scaler, steps=30):
    try:
        pred_scaled = model.forecast(steps=steps)
        pred = inverse_scale(pred_scaled.reshape(-1, 1), scaler).flatten()
        return pred
    except:
        return []
