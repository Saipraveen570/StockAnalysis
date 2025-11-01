import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller

# ---------------- Data Fetch ---------------- #

def get_data(ticker):
    try:
        # 1 year data for speed & stability
        stock_data = yf.download(ticker, period="1y", interval="1d", progress=False)
        if stock_data is None or stock_data.empty:
            return pd.DataFrame()
        return stock_data[["Close"]]
    except Exception:
        return pd.DataFrame()

# ---------------- Stationarity Check ---------------- #

def stationary_check(close_price):
    try:
        adf = adfuller(close_price.dropna())
        return round(adf[1], 4)
    except Exception:
        return 1  # fallback non-stationary

def get_rolling_mean(close_price):
    return close_price.rolling(window=7).mean().dropna()

def get_differencing_order(close_price):
    d = 0
    p_value = stationary_check(close_price)

    # cap differencing to speed up model
    while p_value > 0.05 and d < 2:
        d += 1
        close_price = close_price.diff().dropna()
        p_value = stationary_check(close_price)

    return d

# ---------------- ARIMA Model ---------------- #

def fit_model(data, d):
    # lightweight ARIMA for Streamlit hosting
    order = (3, d, 3)

    model = ARIMA(
        data,
        order=order,
        enforce_stationarity=False,
        enforce_invertibility=False
    )
    
    model_fit = model.fit(maxiter=100, disp=0)

    forecast_steps = 30
    predictions = model_fit.get_forecast(steps=forecast_steps).predicted_mean
    return predictions

# ---------------- Model Evaluation ---------------- #

def evaluate_model(data, d):
    try:
        if len(data) < 60:
            return "N/A"

        train = data[:-30]
        test = data[-30:]

        preds = fit_model(train, d)
        rmse = np.sqrt(mean_squared_error(test, preds))
        return round(rmse, 2)
    except:
        return "N/A"

# ---------------- Scaling ---------------- #

def scaling(close_price):
    scaler = StandardScaler()
    scaled = scaler.fit_transform(close_price.values.reshape(-1, 1))
    return scaled, scaler

def inverse_scaling(scaler, scaled_data):
    return scaler.inverse_transform(np.array(scaled_data).reshape(-1, 1))

# ---------------- Forecast ---------------- #

def get_forecast(data, d):
    preds = fit_model(data, d)

    start = datetime.today()
    dates = [start + timedelta(days=i) for i in range(len(preds))]

    forecast_df = pd.DataFrame({"Close": preds}, index=dates)
    forecast_df.index.name = "Date"
    return forecast_df
