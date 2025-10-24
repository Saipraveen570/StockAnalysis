import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from math import sqrt
from datetime import datetime, timedelta
import streamlit as st


# ------------------------ 1. FETCH STOCK DATA ------------------------
@st.cache_data(show_spinner=False)
def get_data(ticker: str) -> pd.DataFrame:
    """
    Fetches last 6 months of stock closing prices using yfinance.
    """
    try:
        start_date = (datetime.today() - timedelta(days=180)).strftime('%Y-%m-%d')
        data = yf.download(ticker, start=start_date, progress=False)
        if "Close" not in data.columns or data.empty:
            raise ValueError("No close price data found.")
        close_price = data[["Close"]]
        close_price.dropna(inplace=True)
        return close_price
    except Exception as e:
        st.error(f"⚠️ Failed to fetch data for {ticker}: {e}")
        return pd.DataFrame(columns=["Close"])


# ------------------------ 2. MOVING AVERAGE ------------------------
@st.cache_data(show_spinner=False)
def get_rolling_mean(close_price: pd.DataFrame, window: int = 7) -> pd.DataFrame:
    """
    Returns 7-day moving average for smoothing.
    """
    if close_price.empty:
        return pd.DataFrame(columns=["Close"])
    rolling_price = close_price.rolling(window=window).mean().dropna()
    return rolling_price


# ------------------------ 3. DIFFERENCING ORDER ------------------------
def get_differencing_order(data: pd.DataFrame) -> int:
    """
    Dummy differencing order estimator (used to simulate ARIMA behavior).
    """
    return 1 if data["Close"].autocorr(lag=1) > 0.7 else 0


# ------------------------ 4. SCALING ------------------------
def scaling(data: pd.DataFrame):
    """
    Scales Close prices between 0 and 1 for stable model training.
    """
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled = scaler.fit_transform(data)
    scaled_df = pd.DataFrame(scaled, columns=["Close"], index=data.index)
    return scaled_df, scaler


# ------------------------ 5. MODEL EVALUATION ------------------------
def evaluate_model(scaled_data: pd.DataFrame, diff_order: int) -> float:
    """
    Simple Linear Regression evaluation to simulate model accuracy.
    """
    try:
        if len(scaled_data) < 10:
            return 0.0

        data = scaled_data.reset_index()
        data["day"] = np.arange(len(data))
        X = data[["day"]]
        y = data["Close"]

        model = LinearRegression()
        model.fit(X, y)
        preds = model.predict(X)

        rmse = sqrt(mean_squared_error(y, preds))
        return round(rmse, 4)
    except Exception:
        return 0.0


# ------------------------ 6. FORECAST GENERATION ------------------------
def get_forecast(scaled_data: pd.DataFrame, diff_order: int) -> pd.DataFrame:
    """
    Generates next 30-day forecast using Linear Regression trend + noise.
    """
    data = scaled_data.reset_index()
    data["day"] = np.arange(len(data))

    X = data[["day"]]
    y = data["Close"]

    model = LinearRegression()
    model.fit(X, y)

    # Predict next 30 days
    future_days = np.arange(len(data), len(data) + 30).reshape(-1, 1)
    predictions = model.predict(future_days)

    # Add slight variation (noise) to avoid flat or only upward lines
    noise = np.random.normal(0, 0.01, size=predictions.shape)
    final_pred = np.clip(predictions + noise, 0, 1)

    forecast_index = pd.date_range(start=datetime.today(), periods=30)
    forecast_df = pd.DataFrame(final_pred, index=forecast_index, columns=["Close"])

    return forecast_df


# ------------------------ 7. INVERSE SCALING ------------------------
def inverse_scaling(scaler: MinMaxScaler, forecast: pd.Series) -> pd.Series:
    """
    Converts scaled predictions back to actual price values.
    """
    forecast_array = np.array(forecast).reshape(-1, 1)
    return scaler.inverse_transform(forecast_array).flatten()
