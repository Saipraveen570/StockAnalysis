import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler

def get_data(ticker):
    df = yf.download(ticker, period='6mo')
    return df[['Close']]

def get_rolling_mean(df):
    return df.rolling(7).mean().dropna()

def get_differencing_order(df):
    # Placeholder: simple differencing
    return 1

def scaling(df):
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df)
    return pd.DataFrame(scaled, index=df.index, columns=df.columns), scaler

def inverse_scaling(scaler, series):
    return pd.Series(scaler.inverse_transform(series.values.reshape(-1,1)).flatten(), index=series.index)

def evaluate_model(data, order):
    # Dummy RMSE
    return 2.5

def get_forecast(data, order):
    df = data.copy().reset_index()
    df['day'] = np.arange(len(df))
    model = LinearRegression()
    model.fit(df[['day']], df['Close'])
    future_days = np.arange(len(df), len(df)+30).reshape(-1,1)
    pred = model.predict(future_days)
    forecast_index = pd.date_range(start=df['Date'].iloc[-1] + pd.Timedelta(days=1), periods=30)
    return pd.DataFrame(pred, index=forecast_index, columns=['Close'])
