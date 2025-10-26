# utils/model_train.py
import pandas as pd
import yfinance as yf
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler

def get_data(ticker: str) -> pd.DataFrame:
    df = yf.download(ticker, period='1y')
    df = df[['Close']]
    return df

def get_rolling_mean(df: pd.DataFrame, window: int = 7) -> pd.DataFrame:
    df['MA7'] = df['Close'].rolling(window).mean()
    return df

def get_differencing_order(df: pd.DataFrame) -> int:
    # Simple stationarity check
    return 1

def scaling(df: pd.DataFrame):
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df)
    df_scaled = pd.DataFrame(scaled, columns=df.columns, index=df.index)
    return df_scaled, scaler

def inverse_scaling(scaler, series: pd.Series) -> pd.Series:
    return pd.Series(scaler.inverse_transform(series.values.reshape(-1,1)).flatten(), index=series.index)

def evaluate_model(df_scaled: pd.DataFrame, diff_order: int) -> float:
    # Use simple Linear Regression on Close prices
    X = np.arange(len(df_scaled)).reshape(-1,1)
    y = df_scaled['Close'].values
    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)
    rmse = np.sqrt(np.mean((y - y_pred)**2))
    return rmse

def get_forecast(df_scaled: pd.DataFrame, diff_order: int, days: int = 30) -> pd.DataFrame:
    X = np.arange(len(df_scaled)).reshape(-1,1)
    y = df_scaled['Close'].values
    model = LinearRegression()
    model.fit(X, y)
    future_X = np.arange(len(df_scaled), len(df_scaled)+days).reshape(-1,1)
    forecast_values = model.predict(future_X)
    future_index = pd.date_range(df_scaled.index[-1]+pd.Timedelta(days=1), periods=days)
    forecast_df = pd.DataFrame({'Close': forecast_values}, index=future_index)
    return forecast_df
