import yfinance as yf
import pandas as pd
import numpy as np
import joblib
import streamlit as st
import time
from sklearn.preprocessing import MinMaxScaler
from statsmodels.tsa.statespace.sarimax import SARIMAX

# ===============================
# DATA FETCH
# ===============================

@st.cache_data(ttl=300, show_spinner=False)
def get_data(ticker):
    retries = 3
    for r in range(retries):
        try:
            df = yf.download(ticker, period="5y", progress=False, threads=False)
            if not df.empty:
                return df
        except Exception:
            time.sleep(2)
    return pd.DataFrame()

# ===============================
# SCALING
# ===============================

def scale_data(series):
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(series.values.reshape(-1, 1))
    return scaled, scaler

def inverse_scale(scaled_values, scaler):
    return scaler.inverse_transform(scaled_values.reshape(-1, 1)).flatten()

# ===============================
# TRAIN MODEL
# ===============================

@st.cache_resource(show_spinner=False)
def train_model(data):
    close_px = data['Close'].dropna()
    scaled, scaler = scale_data(close_px)

    model = SARIMAX(
        scaled,
        order=(1, 1, 1),
        seasonal_order=(1, 1, 1, 12),
        enforce_stationarity=False,
        enforce_invertibility=False
    )
    
    # Suppress optimizer warnings & increase stability
    try:
        fitted = model.fit(disp=False, maxiter=200)
    except Exception:
        fitted = model.fit(disp=False, method="powell", maxiter=200)

    return fitted, scaler

# ===============================
# SAVE MODEL
# ===============================

def save_model(model, scaler, ticker):
    try:
        joblib.dump(model, f"{ticker}_model.pkl")
        joblib.dump(scaler, f"{ticker}_scaler.pkl")
    except Exception:
        pass  # Streamlit Cloud safe fail

# ===============================
# LOAD MODEL
# ===============================

def load_model(ticker):
    try:
        model = joblib.load(f"{ticker}_model.pkl")
        scaler = joblib.load(f"{ticker}_scaler.pkl")
        return model, scaler
    except Exception:
        return None, None

# ===============================
# FORECAST
# ===============================

def forecast(model, scaler, steps=30):
    try:
        pred_scaled = model.forecast(steps=steps)
        pred = inverse_scale(pred_scaled, scaler)
        return pred
    except Exception:
        return np.array([])
