import numpy as np
import pandas as pd
import yfinance as yf
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
import warnings

warnings.filterwarnings("ignore")

# -------------------------------------------------------
# Helpers
# -------------------------------------------------------
def safe_ticker_symbol(t: str) -> str:
    if not t:
        return ""
    t = t.strip().upper()
    allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-")
    if len(t) > 12 or any(ch not in allowed for ch in t):
        return ""
    return t

# -------------------------------------------------------
# Data loader
# -------------------------------------------------------
def get_data(ticker: str) -> pd.Series:
    ticker = safe_ticker_symbol(ticker)
    if not ticker:
        return pd.Series(dtype=float)

    try:
        data = yf.download(ticker, period="5y", progress=False)
        if "Close" not in data.columns:
            return pd.Series(dtype=float)

        close_price = data["Close"].dropna()
        return close_price
    except Exception:
        return pd.Series(dtype=float)

# -------------------------------------------------------
# Rolling Mean
# -------------------------------------------------------
def get_rolling_mean(series: pd.Series, window: int = 7) -> pd.DataFrame:
    if series.empty or len(series) < window:
        return pd.DataFrame(columns=["Close"])

    df = pd.DataFrame(series)
    df["Close"] = df["Close"].rolling(window).mean()
    df.dropna(inplace=True)
    return df

# -------------------------------------------------------
# Differencing Order (ADF)
# -------------------------------------------------------
def get_differencing_order(df: pd.DataFrame) -> int:
    if df.empty or "Close" not in df.columns:
        return 1

    data = df["Close"].dropna().values
    if len(data) < 20:
        return 1

    try:
        pvalue = adfuller(data)[1]
        return 0 if pvalue <= 0.05 else 1
    except Exception:
        return 1

# -------------------------------------------------------
# Scaling
# -------------------------------------------------------
def scaling(df: pd.DataFrame):
    if df.empty or "Close" not in df.columns:
        return (pd.DataFrame(columns=["Close"]), MinMaxScaler())

    scaler = MinMaxScaler(feature_range=(0, 1))
    try:
        scaled = scaler.fit_transform(df[["Close"]])
        df_scaled = pd.DataFrame(scaled, index=df.index, columns=["Close"])
        return df_scaled, scaler
    except Exception:
        return (pd.DataFrame(columns=["Close"]), MinMaxScaler())

# -------------------------------------------------------
# Model Evaluation (RMSE)
# -------------------------------------------------------
def evaluate_model(scaled_data, d_order: int):
    try:
        if scaled_data.empty or len(scaled_data) < 30:
            return np.nan

        train_size = int(len(scaled_data) * 0.8)
        train, test = scaled_data[:train_size], scaled_data[train_size:]

        model = ARIMA(train, order=(2, d_order, 2))
        model_fit = model.fit()

        preds = model_fit.forecast(steps=len(test))
        rmse = np.sqrt(mean_squared_error(test, preds))
        return rmse
    except Exception:
        return np.nan

# -------------------------------------------------------
# Forecast
# -------------------------------------------------------
def get_forecast(scaled_data, d_order: int, steps: int = 30) -> pd.DataFrame:
    if scaled_data.empty:
        return pd.DataFrame(columns=["Close"])

    try:
        model = ARIMA(scaled_data, order=(2, d_order, 2))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=steps)
        future_index = pd.date_range(start=scaled_data.index[-1], periods=steps+1, freq="D")[1:]
        return pd.DataFrame(forecast, index=future_index, columns=["Close"])
    except Exception:
        # Return flat forecast fallback
        last_val = float(scaled_data["Close"].iloc[-1]) if not scaled_data.empty else 0
        future_index = pd.date_range(start=pd.Timestamp.today(), periods=steps, freq="D")
        return pd.DataFrame([last_val]*steps, index=future_index, columns=["Close"])

# -------------------------------------------------------
# Inverse Scale
# -------------------------------------------------------
def inverse_scaling(scaler, values):
    try:
        arr = np.array(values).reshape(-1, 1)
        return scaler.inverse_transform(arr).flatten()
    except Exception:
        return values
