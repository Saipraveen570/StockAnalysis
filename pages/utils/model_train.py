import yfinance as yf
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.arima.model import ARIMA
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def get_data(ticker):
    start_date = (datetime.today() - timedelta(days=180)).strftime('%Y-%m-%d')
    stock_data = yf.download(ticker, start=start_date)
    return stock_data[['Close']]

def stationary_check(close_price):
    adf_test = adfuller(close_price)
    return round(adf_test[1], 3)

def get_rolling_mean(close_price):
    return close_price.rolling(window=7).mean().dropna()

def get_differencing_order(close_price):
    p_value = stationary_check(close_price)
    d = 0
    while p_value > 0.05 and d < 2:  # limit differencing to avoid overfitting
        d += 1
        close_price = close_price.diff().dropna()
        p_value = stationary_check(close_price)
    return d

def fit_model(data, differencing_order):
    model = ARIMA(data, order=(5, differencing_order, 2))  # optimized order
    model_fit = model.fit()
    forecast = model_fit.get_forecast(steps=30)
    return forecast.predicted_mean

def evaluate_model(original_price, differencing_order):
    train, test = original_price[:-30], original_price[-30:]
    predictions = fit_model(train, differencing_order)
    rmse = np.sqrt(mean_squared_error(test, predictions))
    return round(rmse, 2)

def get_forecast(original_price, differencing_order):
    predictions = fit_model(original_price, differencing_order)
    forecast_index = pd.date_range(start=datetime.today(), periods=30)
    return pd.DataFrame(predictions, index=forecast_index, columns=['Close'])
