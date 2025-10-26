import yfinance as yf
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler
from datetime import timedelta
import numpy as np
import pandas as pd

# -------------------------
# Data fetching
# -------------------------
def get_data(ticker):
    """Fetches historical closing price data from Yahoo Finance."""
    stock_data = yf.download(ticker, start='2024-01-01')
    if stock_data.empty:
        raise ValueError(f"No data found for ticker {ticker}")
    return stock_data[['Close']]

# -------------------------
# Stationarity check
# -------------------------
def stationary_check(series):
    """Returns the p-value of Augmented Dickey-Fuller test."""
    series = series.dropna()
    if len(series) < 10:
        return 0  # Assume stationary if too little data
    adf_test = adfuller(series)
    p_value = round(adf_test[1], 3)
    return p_value

# -------------------------
# Rolling mean
# -------------------------
def get_rolling_mean(close_price, window=7):
    rolling_price = close_price.rolling(window=window).mean().dropna()
    return rolling_price

# -------------------------
# Determine differencing order
# -------------------------
def get_differencing_order(close_price):
    series = close_price.copy()
    d = 0
    p_value = stationary_check(series)
    while p_value > 0.05:
        series = series.diff().dropna()
        p_value = stationary_check(series)
        d += 1
        if d > 5:  # prevent infinite loop
            break
    return d

# -------------------------
# Fit ARIMA model
# -------------------------
def fit_model(series, differencing_order, ar_order=5, ma_order=5, forecast_steps=30):
    """
    Fit ARIMA model and return forecast.
    ar_order & ma_order kept small for faster and stable computation.
    """
    series = series.squeeze()  # convert DataFrame to Series if needed
    model = ARIMA(series, order=(ar_order, differencing_order, ma_order))
    model_fit = model.fit()
    forecast = model_fit.get_forecast(steps=forecast_steps)
    return forecast.predicted_mean

# -------------------------
# Evaluate model
# -------------------------
def evaluate_model(series, differencing_order):
    series = series.squeeze()
    if len(series) < 60:
        return np.nan
    train_data = series[:-30]
    test_data = series[-30:]
    pred = fit_model(train_data, differencing_order)
    rmse = np.sqrt(mean_squared_error(test_data, pred))
    return round(rmse, 2)

# -------------------------
# Scaling / inverse scaling
# -------------------------
def scaling(series):
    scaler = StandardScaler()
    scaled = scaler.fit_transform(series.values.reshape(-1, 1))
    return scaled, scaler

def inverse_scaling(scaler, scaled_values):
    return scaler.inverse_transform(np.array(scaled_values).reshape(-1, 1))

# -------------------------
# Forecast next 30 days
# -------------------------
def get_forecast(series, differencing_order):
    series = series.squeeze()
    pred = fit_model(series, differencing_order)
    last_date = series.index[-1]
    forecast_index = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=len(pred), freq='D')
    forecast_df = pd.DataFrame(pred, index=forecast_index, columns=['Close'])
    return forecast_df
