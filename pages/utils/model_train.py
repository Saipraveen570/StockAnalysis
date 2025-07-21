import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import streamlit as st


# ------------------------- 1. Data Fetching -------------------------

@st.cache_data
def get_data(ticker):
    """
    Fetch historical stock closing prices using yfinance.
    """
    end = datetime.today()
    start = end - timedelta(days=730)  # 2 years of data
    df = yf.download(ticker, start=start, end=end)
    return df['Close'].dropna()


# ------------------------- 2. Smoothing -------------------------

def get_rolling_mean(series, window=5):
    """
    Smooths series with a rolling mean.
    """
    return series.rolling(window=window).mean().dropna()


# ------------------------- 3. Differencing Order Estimation -------------------------

def get_differencing_order(series):
    """
    Calculates optimal differencing order (d) using ADF test.
    """
    from statsmodels.tsa.stattools import adfuller
    d = 0
    pvalue = adfuller(series)[1]
    while pvalue > 0.05 and d < 2:
        series = series.diff().dropna()
        pvalue = adfuller(series)[1]
        d += 1
    return d


# ------------------------- 4. Scaling -------------------------

def scaling(series):
    """
    Scales data using MinMaxScaler.
    """
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled = scaler.fit_transform(np.array(series).reshape(-1, 1))
    return pd.Series(scaled.flatten(), index=series.index), scaler


def inverse_scaling(scaler, series):
    """
    Inverts MinMaxScaler transformation.
    """
    inv = scaler.inverse_transform(np.array(series).reshape(-1, 1))
    return pd.Series(inv.flatten(), index=series.index)


# ------------------------- 5. Model Evaluation -------------------------

def evaluate_model(series, d):
    """
    Trains SARIMAX model and returns RMSE on last 30-day prediction.
    """
    train = series[:-30]
    test = series[-30:]
    
    model = SARIMAX(train, order=(1, d, 1), enforce_stationarity=False, enforce_invertibility=False)
    results = model.fit(disp=False)
    forecast = results.forecast(steps=30)

    rmse = np.sqrt(mean_squared_error(test, forecast))
    return rmse


# ------------------------- 6. Forecasting -------------------------

@st.cache_data
def get_forecast(series, d):
    """
    Trains SARIMAX and forecasts next 30 days.
    """
    series = series[-365:]  # Use only last 1 year for faster training
    model = SARIMAX(series, order=(1, d, 1), enforce_stationarity=False, enforce_invertibility=False)
    results = model.fit(disp=False)
    preds = results.forecast(steps=30)

    future_dates = pd.date_range(start=datetime.today(), periods=30, freq='D')
    forecast_df = pd.DataFrame(preds, index=future_dates, columns=['Close'])

    return forecast_df
