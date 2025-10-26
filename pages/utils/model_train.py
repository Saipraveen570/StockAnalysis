import yfinance as yf
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.preprocessing import MinMaxScaler

# -------------------------------
# Get historical Close price
# -------------------------------
def get_data(ticker: str):
    df = yf.download(ticker, period='max')
    return df[['Close']].copy()

# -------------------------------
# Rolling Mean
# -------------------------------
def get_rolling_mean(df: pd.DataFrame, window: int = 7):
    df_rm = df.rolling(window).mean().dropna()
    return df_rm

# -------------------------------
# Differencing order (ARIMA)
# -------------------------------
def get_differencing_order(df: pd.DataFrame):
    # Simple approach: 1 for non-stationary series
    return 1

# -------------------------------
# Scale data
# -------------------------------
def scaling(df: pd.DataFrame):
    scaler = MinMaxScaler()
    scaled = pd.DataFrame(scaler.fit_transform(df), index=df.index, columns=df.columns)
    return scaled, scaler

# -------------------------------
# Evaluate model (dummy ARIMA prediction)
# -------------------------------
def evaluate_model(df_scaled: pd.DataFrame, d: int):
    model = ARIMA(df_scaled, order=(5, d, 0))
    fitted = model.fit()
    pred = fitted.fittedvalues
    rmse = np.sqrt(np.mean((df_scaled.values.flatten() - pred.flatten())**2))
    return rmse

# -------------------------------
# Forecast next 30 days
# -------------------------------
def get_forecast(df_scaled: pd.DataFrame, d: int, steps: int = 30):
    model = ARIMA(df_scaled, order=(5, d, 0))
    fitted = model.fit()
    forecast_values = fitted.forecast(steps=steps)
    future_dates = pd.date_range(start=df_scaled.index[-1], periods=steps+1, freq='D')[1:]
    forecast_df = pd.DataFrame(forecast_values, index=future_dates, columns=['Close'])
    return forecast_df

# -------------------------------
# Inverse scaling
# -------------------------------
def inverse_scaling(scaler, df: pd.DataFrame):
    inv = pd.DataFrame(scaler.inverse_transform(df), index=df.index, columns=df.columns)
    return inv
