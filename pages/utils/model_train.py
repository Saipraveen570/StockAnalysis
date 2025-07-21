import pandas as pd
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.preprocessing import MinMaxScaler
import numpy as np

# ========== Data Preprocessing ==========

def get_data(ticker):
    import yfinance as yf
    df = yf.download(ticker, period="2y")
    df = df[['Close']].dropna()
    df.index = pd.to_datetime(df.index)
    return df

def get_rolling_mean(df, window=5):
    df = df.copy()
    df['Close'] = df['Close'].rolling(window).mean()
    return df.dropna()

def get_differencing_order(df):
    from pmdarima.arima.utils import ndiffs
    return ndiffs(df['Close'], test='adf')

def scaling(df):
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df[['Close']])
    df_scaled = pd.DataFrame(scaled, index=df.index, columns=['Close'])
    return df_scaled, scaler

def inverse_scaling(scaler, data):
    return scaler.inverse_transform(data.values.reshape(-1, 1)).flatten()

# ========== Model Training ==========

def evaluate_model(df_scaled, d):
    train = df_scaled.iloc[:-30]
    test = df_scaled.iloc[-30:]

    model = SARIMAX(train['Close'], order=(1, d, 1), enforce_stationarity=False, enforce_invertibility=False)
    results = model.fit(disp=False)

    forecast = results.forecast(steps=len(test))
    rmse = mean_squared_error(test['Close'], forecast, squared=False)
    return round(rmse, 4)

def get_forecast(df_scaled, d):
    model = SARIMAX(df_scaled['Close'], order=(1, d, 1), enforce_stationarity=False, enforce_invertibility=False)
    results = model.fit(disp=False)

    forecast = results.forecast(steps=30)
    forecast_dates = pd.date_range(start=df_scaled.index[-1] + pd.Timedelta(days=1), periods=30)
    forecast_df = pd.DataFrame(forecast, columns=['Close'])
    forecast_df.index = forecast_dates
    return forecast_df
