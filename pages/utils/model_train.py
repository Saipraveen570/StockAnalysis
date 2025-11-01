import yfinance as yf
import numpy as np
import pandas as pd
import time
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.preprocessing import MinMaxScaler
import streamlit as st

# ------------------ DATA FETCH ------------------ #
@st.cache_data(show_spinner=False, ttl=300)
def get_data(ticker):
    retries = 4
    for _ in range(retries):
        try:
            df = yf.download(ticker, period="5y", auto_adjust=True, progress=False, threads=False)
            if not df.empty:
                return df[["Close"]]
        except Exception:
            time.sleep(2)
    return pd.DataFrame()

# ------------------ TRANSFORM FUNCTIONS ------------------ #
def get_rolling_mean(close_df, window=3):
    return close_df["Close"].rolling(window=window).mean().dropna().to_frame()

def get_differencing_order(series):
    # Fallback safe differencing
    return 1

def scaling(series):
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(series.values.reshape(-1,1))
    return scaled, scaler

def inverse_scaling(scaler, arr):
    return scaler.inverse_transform(np.array(arr).reshape(-1,1))

# ------------------ MODEL ------------------ #
def train_model(data):
    model = SARIMAX(data, order=(1,1,1), seasonal_order=(1,1,1,12), enforce_stationarity=False, enforce_invertibility=False)
    results = model.fit(disp=False)
    return results

def evaluate_model(data, d_order):
    try:
        model = SARIMAX(data, order=(1, d_order, 1), seasonal_order=(1,1,1,12),
                         enforce_stationarity=False, enforce_invertibility=False)
        results = model.fit(disp=False)
        fitted_vals = results.fittedvalues
        rmse = np.sqrt(np.mean((data[d_order:] - fitted_vals[d_order:])**2))
        return round(float(rmse), 4)
    except Exception:
        return None

def get_forecast(data, d_order, steps=30):
    try:
        model = SARIMAX(data, order=(1, d_order, 1), seasonal_order=(1,1,1,12),
                         enforce_stationarity=False, enforce_invertibility=False)
        results = model.fit(disp=False)
        forecast_scaled = results.forecast(steps)
        idx = pd.date_range(start=pd.Timestamp.today(), periods=steps, freq='B')
        forecast_df = pd.DataFrame({"Close": forecast_scaled}, index=idx)
        return forecast_df
    except Exception:
        return pd.DataFrame()
