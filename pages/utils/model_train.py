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
    """Fetch historical stock closing prices."""
    try:
        data = yf.download(ticker, start="2020-01-01")
        data = data[['Close']].dropna()
        data.index = pd.to_datetime(data.index)
        return data
    except Exception as e:
        st.error(f"❌ Unable to fetch data for {ticker}. Error: {e}")
        st.stop()


# ------------------------------------------------------
# 2️⃣ DATA PREPROCESSING
# ------------------------------------------------------
def get_rolling_mean(df: pd.DataFrame, window: int = 7):
    """Compute rolling mean to smooth short-term fluctuations."""
    df_copy = df.copy()
    df_copy['Close'] = df_copy['Close'].rolling(window=window, min_periods=1).mean()
    return df_copy


def get_differencing_order(df: pd.DataFrame):
    """Return differencing order (fixed to 1 for simplicity)."""
    return 1


def scaling(df: pd.DataFrame):
    """Normalize Close prices between 0 and 1."""
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df[['Close']])
    scaled_df = pd.DataFrame(scaled, index=df.index, columns=['Close'])
    return scaled_df, scaler


def inverse_scaling(scaler, series):
    """Revert scaled values to original price scale."""
    scaled_array = np.array(series).reshape(-1, 1)
    return scaler.inverse_transform(scaled_array)


# ------------------------------------------------------
# 3️⃣ MODEL TRAINING / EVALUATION
# ------------------------------------------------------
def evaluate_model(scaled_df: pd.DataFrame, diff_order: int = 1):
    """Train Linear Regression and compute RMSE."""
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
# 4️⃣ FORECASTING (NEXT 30 DAYS)
# ------------------------------------------------------
def get_forecast(scaled_df: pd.DataFrame, diff_order: int = 1, forecast_days: int = 30):
    """Generate next N-day forecast using Linear Regression + 7-day MA."""
    df = scaled_df.copy()
    df['Target'] = df['Close'].shift(-1)
    df.dropna(inplace=True)

    X = np.arange(len(df)).reshape(-1, 1)
    y = df['Target'].values

    model = LinearRegression()
    model.fit(X, y)

    # Predict next N days
    future_X = np.arange(len(df), len(df) + forecast_days).reshape(-1, 1)
    future_preds = model.predict(future_X)

    # Apply simple moving average for smoothing
    ma_window = 7
    final_preds = np.convolve(future_preds, np.ones(ma_window) / ma_window, mode='same')

    # Align index with future dates (business days)
    last_date = df.index[-1]
    forecast_index = pd.date_range(start=last_date, periods=forecast_days + 1, freq='B')[1:]

    forecast_df = pd.DataFrame(final_preds, index=forecast_index, columns=['Close'])
    return forecast_df
