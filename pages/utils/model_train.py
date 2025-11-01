import yfinance as yf
import numpy as np
import pandas as pd
import time
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.preprocessing import MinMaxScaler
import joblib
import streamlit as st

@st.cache_data(show_spinner=False)
def get_data(ticker):
    retries = 5
    for i in range(retries):
        try:
            df = yf.download(ticker, period="5y", progress=False, threads=False)
            if not df.empty:
                return df
        except Exception:
            time.sleep(2)
    st.error(f"⚠️ Unable to fetch data for {ticker}. Try again later.")
    return pd.DataFrame()

def scaling(series):
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(series.values.reshape(-1,1))
    return scaled, scaler

def inverse_scaling(scaled, scaler):
    return scaler.inverse_transform(scaled)

def train_model(data):
    close_data = data["Close"]
    scaled, scaler = scaling(close_data)
    model = SARIMAX(scaled, order=(1,1,1), seasonal_order=(1,1,1,12))
    results = model.fit(disp=False)
    return results, scaler

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

def forecast(model, scaler, steps=30):
    pred_scaled = model.forecast(steps=steps)
    pred = inverse_scaling(pred_scaled.reshape(-1,1), scaler).flatten()
    return pred
