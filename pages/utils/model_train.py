# pages/utils/model_train.py

import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.preprocessing import MinMaxScaler

# -------------------------------
# Fetch historical stock data
# -------------------------------
def get_data(ticker):
    """Fetches historical stock Close prices from Yahoo Finance"""
    import yfinance as yf
    df = yf.download(ticker, period='5y')
    df = df[['Close']]
    df.dropna(inplace=True)
    return df

# -------------------------------
# Rolling mean smoothing
# -------------------------------
def get_rolling_mean(df, window=7):
    """Computes rolling mean to smooth the series"""
    rolling = df.copy()
    rolling['Close'] = rolling['Close'].rolling(window).mean()
    rolling.dropna(inplace=True)
    return rolling

# -------------------------------
# Determine differencing order for ARIMA
# -------------------------------
def get_differencing_order(df):
    """Returns 1 if differencing is needed, 0 otherwise"""
    # Simple heuristic: check for stationarity using Augmented Dickey-Fuller
    from statsmodels.tsa.stattools import adfuller
    result = adfuller(df['Close'])
    return 0 if result[1] < 0.05 else 1

# -------------------------------
# Scaling for modeling
# -------------------------------
def scaling(df):
    """Scales data using MinMaxScaler"""
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled = scaler.fit_transform(df[['Close']])
    scaled_df = pd.DataFrame(scaled, index=df.index, columns=['Close'])
    return scaled_df, scaler

def inverse_scaling(scaler, data):
    """Inverse transform scaled data"""
    return pd.DataFrame(scaler.inverse_transform(data.values.reshape(-1,1)), index=data.index, columns=['Close'])

# -------------------------------
# Evaluate ARIMA model
# -------------------------------
def evaluate_model(df_scaled, differencing_order):
    """
    Fits an ARIMA model and calculates RMSE on training data
    df_scaled: scaled dataframe
    differencing_order: int, ARIMA differencing order
    """
    df_scaled_values = df_scaled['Close'].to_numpy()
    
    try:
        model = ARIMA(df_scaled_values, order=(5, differencing_order, 0))
        model_fit = model.fit()
        pred = model_fit.fittedvalues

        # Ensure pred is numpy array
        pred = np.array(pred)

        rmse = np.sqrt(np.mean((df_scaled_values.flatten() - pred.flatten())**2))
        return rmse
    except Exception as e:
        print("ARIMA evaluation error:", e)
        return np.nan

# -------------------------------
# Forecast next 30 days
# -------------------------------
def get_forecast(df_scaled, differencing_order, steps=30):
    """Generates forecast for next 'steps' days using ARIMA"""
    df_scaled_values = df_scaled['Close'].to_numpy()

    model = ARIMA(df_scaled_values, order=(5, differencing_order, 0))
    model_fit = model.fit()
    forecast_values = model_fit.forecast(steps=steps)

    last_index = df_scaled.index[-1]
    future_index = pd.date_range(start=last_index + pd.Timedelta(days=1), periods=steps, freq='B')
    forecast_df = pd.DataFrame(forecast_values, index=future_index, columns=['Close'])
    return forecast_df
