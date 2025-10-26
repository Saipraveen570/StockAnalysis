import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from statsmodels.tsa.arima.model import ARIMA

# Fetch stock data
def get_data(ticker):
    import yfinance as yf
    df = yf.download(ticker, period="max")
    return df[['Close']]

# Rolling mean for smoothing
def get_rolling_mean(df, window=7):
    df_rolled = df.copy()
    df_rolled['Close'] = df['Close'].rolling(window).mean()
    df_rolled.dropna(inplace=True)
    return df_rolled

# Determine differencing order (for ARIMA)
def get_differencing_order(df):
    return 1  # Simple fixed differencing

# Scale data
def scaling(df):
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df)
    return pd.DataFrame(scaled, columns=df.columns, index=df.index), scaler

# Evaluate model (RMSE)
def evaluate_model(df_scaled, diff_order):
    model = ARIMA(df_scaled, order=(1,diff_order,0))
    model_fit = model.fit()
    pred = model_fit.predict()
    rmse = np.sqrt(np.mean((df_scaled.values.flatten() - pred.flatten())**2))
    return rmse

# Forecast next 30 days
def get_forecast(df_scaled, diff_order):
    model = ARIMA(df_scaled, order=(1,diff_order,0))
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=30)
    forecast_df = pd.DataFrame(forecast, columns=['Close'])
    forecast_df.index = pd.date_range(start=df_scaled.index[-1]+pd.Timedelta(days=1), periods=30)
    return forecast_df

# Inverse scale
def inverse_scaling(scaler, series):
    series = series.values.reshape(-1,1)
    inv = scaler.inverse_transform(series)
    return pd.Series(inv.flatten(), index=series.index)
