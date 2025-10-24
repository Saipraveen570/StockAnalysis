import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import streamlit as st

# ------------------------------------------------------
# 1️⃣ DATA FETCHING
# ------------------------------------------------------
@st.cache_data(show_spinner=False)
def get_data(ticker: str):
    """Fetch stock historical close prices."""
    data = yf.download(ticker, start="2020-01-01")
    data = data[['Close']].dropna()
    data.index = pd.to_datetime(data.index)
    return data


# ------------------------------------------------------
# 2️⃣ DATA TRANSFORMATION
# ------------------------------------------------------
def get_rolling_mean(df, window=7):
    """Compute rolling mean for smoothing short-term noise."""
    df_rolling = df.copy()
    df_rolling['Close'] = df_rolling['Close'].rolling(window=window, min_periods=1).mean()
    return df_rolling


def get_differencing_order(df):
    """Determine differencing order (fixed to 1 for simplicity)."""
    return 1


def scaling(df):
    """Normalize values between 0 and 1."""
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df[['Close']])
    scaled_df = pd.DataFrame(scaled, index=df.index, columns=['Close'])
    return scaled_df, scaler


def inverse_scaling(scaler, series):
    """Revert scaled values to original price scale."""
    scaled = np.array(series).reshape(-1, 1)
    return scaler.inverse_transform(scaled)


# ------------------------------------------------------
# 3️⃣ MODEL TRAINING
# ------------------------------------------------------
def evaluate_model(scaled_df, diff_order=1):
    """Train Linear Regression model and compute RMSE."""
    df = scaled_df.copy()
    df['Target'] = df['Close'].shift(-1)
    df.dropna(inplace=True)

    X = np.arange(len(df)).reshape(-1, 1)
    y = df['Target'].values

    model = LinearRegression()
    model.fit(X, y)

    preds = model.predict(X)
    rmse = np.sqrt(mean_squared_error(y, preds))
    return rmse


# ------------------------------------------------------
# 4️⃣ FORECASTING (Next 30 Days)
# ------------------------------------------------------
def get_forecast(scaled_df, diff_order=1, forecast_days=30):
    """Generate next N days forecast using Linear Regression trend + moving average."""
    df = scaled_df.copy()
    df['Target'] = df['Close'].shift(-1)
    df.dropna(inplace=True)

    X = np.arange(len(df)).reshape(-1, 1)
    y = df['Target'].values

    model = LinearRegression()
    model.fit(X, y)

    # Predict next N days based on trend
    future_X = np.arange(len(df), len(df) + forecast_days).reshape(-1, 1)
    future_preds = model.predict(future_X)

    # Apply simple moving average for smoother forecast
    ma_window = 7
    final_pred = np.convolve(future_preds, np.ones(ma_window) / ma_window, mode='same')

    # Align index with future dates
    last_date = df.index[-1]
    forecast_index = pd.date_range(start=last_date, periods=forecast_days + 1, freq='B')[1:]

    forecast_df = pd.DataFrame(final_pred, index=forecast_index, columns=['Close'])
    return forecast_df
