import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

# -------------------------------
# 1️⃣ Fetch stock data
# -------------------------------
def get_data(ticker: str) -> pd.DataFrame:
    """
    Download last 6 months of closing prices for the ticker.
    """
    df = yf.download(ticker, period='6mo')
    return df[['Close']]

# -------------------------------
# 2️⃣ Rolling mean (7-day)
# -------------------------------
def get_rolling_mean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute 7-day moving average of close prices.
    """
    return df.rolling(7).mean().dropna()

# -------------------------------
# 3️⃣ Differencing order (placeholder)
# -------------------------------
def get_differencing_order(df: pd.DataFrame) -> int:
    """
    Placeholder for differencing order.
    """
    return 1

# -------------------------------
# 4️⃣ Scaling
# -------------------------------
def scaling(df: pd.DataFrame):
    """
    Scale data to 0-1 range using MinMaxScaler.
    """
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df)
    return pd.DataFrame(scaled, index=df.index, columns=df.columns), scaler

# -------------------------------
# 5️⃣ Inverse scaling
# -------------------------------
def inverse_scaling(scaler, series: pd.Series) -> pd.Series:
    """
    Convert scaled values back to original scale.
    """
    return pd.Series(scaler.inverse_transform(series.values.reshape(-1, 1)).flatten(), index=series.index)

# -------------------------------
# 6️⃣ Evaluate model (RMSE)
# -------------------------------
def evaluate_model(data: pd.DataFrame, order: int) -> float:
    """
    Compute RMSE using a simple train/test split.
    """
    df = data.copy().reset_index()
    df['day'] = np.arange(len(df))
    
    # Use last 10 days as test
    train_df = df.iloc[:-10]
    test_df = df.iloc[-10:]
    
    X_train = train_df[['day']]
    y_train = train_df['Close']
    X_test = test_df[['day']]
    y_test = test_df['Close']
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    return rmse

# -------------------------------
# 7️⃣ Forecasting using Linear Regression
# -------------------------------
def get_forecast(data: pd.DataFrame, order: int) -> pd.DataFrame:
    """
    Forecast next 30 days using Linear Regression on rolling data.
    """
    df = data.copy().reset_index()
    df['day'] = np.arange(len(df))

    X = df[['day']]
    y = df['Close']

    model = LinearRegression()
    model.fit(X, y)

    # Predict next 30 days
    future_days = np.arange(len(df), len(df) + 30).reshape(-1, 1)
    predictions = model.predict(future_days)

    forecast_index = pd.date_range(start=df['Date'].iloc[-1] + pd.Timedelta(days=1), periods=30)
    return pd.DataFrame(predictions, index=forecast_index, columns=['Close'])
