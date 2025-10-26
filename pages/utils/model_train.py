import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.preprocessing import MinMaxScaler

# -------------------------------
# Fetch historical close prices
# -------------------------------
def get_data(ticker):
    import yfinance as yf
    df = yf.download(ticker, period="5y")
    return df[['Close']]

# -------------------------------
# Rolling mean
# -------------------------------
def get_rolling_mean(df, window=7):
    df_rolled = df.copy()
    df_rolled['Close'] = df['Close'].rolling(window=window).mean().dropna()
    return df_rolled.dropna()

# -------------------------------
# Differencing order for ARIMA
# -------------------------------
def get_differencing_order(df):
    # Simple heuristic
    return 1 if len(df) > 50 else 0

# -------------------------------
# Scaling data
# -------------------------------
def scaling(df):
    scaler = MinMaxScaler(feature_range=(0,1))
    scaled = scaler.fit_transform(df[['Close']])
    df_scaled = pd.DataFrame(scaled, index=df.index, columns=['Close'])
    return df_scaled, scaler

# -------------------------------
# Inverse scaling
# -------------------------------
def inverse_scaling(scaler, series):
    return pd.Series(scaler.inverse_transform(series.values.reshape(-1,1)).flatten(), index=series.index)

# -------------------------------
# Evaluate ARIMA model
# -------------------------------
def evaluate_model(df_scaled, order):
    model = ARIMA(df_scaled['Close'], order=(order,0,0))
    model_fit = model.fit()
    pred = model_fit.fittedvalues
    y_true = df_scaled['Close'].values
    rmse = np.sqrt(np.mean((y_true - pred)**2))
    return rmse

# -------------------------------
# Forecast next 30 days
# -------------------------------
def get_forecast(df_scaled, order, steps=30):
    model = ARIMA(df_scaled['Close'], order=(order,0,0))
    model_fit = model.fit()
    forecast_vals = model_fit.forecast(steps=steps)
    last_index = df_scaled.index[-1]
    future_index = pd.date_range(start=last_index + pd.Timedelta(days=1), periods=steps)
    forecast_df = pd.DataFrame(forecast_vals, index=future_index, columns=['Close'])
    return forecast_df
