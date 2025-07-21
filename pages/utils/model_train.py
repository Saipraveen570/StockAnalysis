import yfinance as yf
import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

# 1. Get stock data
def get_data(ticker):
    try:
        df = yf.download(ticker, period='1y', interval='1d', progress=False)
        if df.empty or 'Close' not in df.columns:
            raise ValueError("No close price data available.")
        close_price = df['Close']
        return close_price.to_frame(name='Close')
    except Exception as e:
        print(f"Error downloading stock data: {e}")
        return pd.DataFrame(columns=['Close'])

# 2. Get rolling mean
def get_rolling_mean(data, window=7):
    return data.rolling(window=window).mean().dropna()

# 3. Determine differencing order
def get_differencing_order(data):
    return 1 if data['Close'].diff().dropna().autocorr() > 0.2 else 0

# 4. Scaling
def scaling(data):
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(data)
    scaled_df = pd.DataFrame(scaled, index=data.index, columns=['Close'])
    return scaled_df, scaler

# 5. Inverse scaling
def inverse_scaling(scaler, data):
    return scaler.inverse_transform(data.values.reshape(-1, 1)).flatten()

# 6. Evaluate SARIMAX model
def evaluate_model(data, d):
    try:
        train = data[:-30]
        test = data[-30:]
        model = SARIMAX(train, order=(1,d,1), seasonal_order=(0,0,0,0))
        model_fit = model.fit(disp=False)
        preds = model_fit.predict(start=len(train), end=len(data)-1)
        rmse = np.sqrt(mean_squared_error(test, preds))
        return round(rmse, 4)
    except Exception as e:
        print(f"Model evaluation failed: {e}")
        return np.nan

# 7. Forecast future values
def get_forecast(data, d):
    try:
        model = SARIMAX(data, order=(1,d,1), seasonal_order=(0,0,0,0))
        model_fit = model.fit(disp=False)
        preds = model_fit.forecast(steps=30)
        start_date = datetime.now().strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=29)).strftime('%Y-%m-%d')
        forecast_index = pd.date_range(start=start_date, end=end_date, freq='D')
        return pd.DataFrame(preds, index=forecast_index, columns=['Close'])
    except Exception as e:
        print(f"Forecasting failed: {e}")
        return pd.DataFrame(columns=['Close'])
