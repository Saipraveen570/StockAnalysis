import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.statespace.sarimax import SARIMAX
import streamlit as st
import warnings
warnings.filterwarnings("ignore")


# ------------------- 1. GET DATA -------------------
@st.cache_data(ttl=3600)
def get_data(ticker):
    try:
        df = yf.download(ticker, period="2y")
        return df['Close'].dropna().to_frame(name='Close')
    except Exception as e:
        st.error(f"Error downloading stock data: {e}")
        return None


# ------------------- 2. SMOOTHING -------------------
def get_rolling_mean(df, window=3):
    return df.rolling(window=window).mean().dropna()


# ------------------- 3. STATIONARITY -------------------
def get_differencing_order(df):
    for d in range(3):  # test for 0, 1, 2
        try:
            result = adfuller(df.diff(d).dropna())
            if result[1] < 0.05:
                return d
        except:
            continue
    return 1  # fallback


# ------------------- 4. SCALING -------------------
@st.cache_resource
def scaling(df):
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df)
    return pd.Series(scaled.flatten(), index=df.index), scaler


def inverse_scaling(scaler, data):
    return scaler.inverse_transform(data.values.reshape(-1, 1)).flatten()


# ------------------- 5. EVALUATE MODEL -------------------
@st.cache_data
def evaluate_model(series, d):
    try:
        model = SARIMAX(series, order=(1, d, 1), enforce_stationarity=False, enforce_invertibility=False)
        result = model.fit(disp=False)
        pred = result.predict(start=0, end=len(series) - 1)
        rmse = np.sqrt(mean_squared_error(series, pred))
        return rmse
    except Exception as e:
        st.error(f"Model evaluation failed: {e}")
        return np.nan
