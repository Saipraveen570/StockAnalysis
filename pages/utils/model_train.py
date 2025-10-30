import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

# ---------------------------------
# ✅ Safe Ticker Normalization
# ---------------------------------
def _safe_ticker(ticker: str) -> str:
    if not ticker:
        return ""
    ticker = str(ticker).upper().strip()
    allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-")
    if len(ticker) > 12 or any(c not in allowed for c in ticker):
        return ""
    return ticker

# ---------------------------------
# ✅ Safe yfinance download
# ---------------------------------
def get_data(ticker: str) -> pd.DataFrame:
    """
    Download last 6 months close price. Returns empty df on failure.
    """
    t = _safe_ticker(ticker)
    if not t:
        return pd.DataFrame()

    try:
        df = yf.download(t, period="6mo", progress=False)
        if df.empty or "Close" not in df.columns:
            return pd.DataFrame()
        return df[["Close"]].dropna()
    except Exception:
        return pd.DataFrame()

# ---------------------------------
# ✅ Rolling mean (7-day)
# ---------------------------------
def get_rolling_mean(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "Close" not in df.columns:
        return pd.DataFrame()
    try:
        rm = df.rolling(7).mean().dropna()
        return rm
    except Exception:
        return pd.DataFrame()

# ---------------------------------
# ✅ Differencing order placeholder
# ---------------------------------
def get_differencing_order(df: pd.DataFrame) -> int:
    return 1

# ---------------------------------
# ✅ Safe scaling
# ---------------------------------
def scaling(df: pd.DataFrame):
    """
    Returns (scaled_df, scaler). Returns empty df if input invalid.
    """
    if df.empty:
        return pd.DataFrame(), None
    try:
        scaler = MinMaxScaler()
        scaled = scaler.fit_transform(df.values)
        return pd.DataFrame(scaled, index=df.index, columns=df.columns), scaler
    except Exception:
        return pd.DataFrame(), None

# ---------------------------------
# ✅ Safe inverse scaling
# ---------------------------------
def inverse_scaling(scaler, series: pd.Series) -> pd.Series:
    if scaler is None or series.empty:
        return series
    try:
        values = series.values.reshape(-1, 1)
        inv = scaler.inverse_transform(values).flatten()
        return pd.Series(inv, index=series.index)
    except Exception:
        return series

# ---------------------------------
# ✅ Evaluate model safely (RMSE)
# ---------------------------------
def evaluate_model(data: pd.DataFrame, order: int) -> float:
    """
    Evaluate via last 10 days RMSE. Returns np.nan if invalid.
    """
    if data.empty or "Close" not in data.columns or len(data) < 15:
        return np.nan

    try:
        df = data.copy().reset_index(drop=True)
        df["day"] = np.arange(len(df))

        train_df = df.iloc[:-10]
        test_df = df.iloc[-10:]

        model = LinearRegression()
        model.fit(train_df[["day"]], train_df["Close"])

        preds = model.predict(test_df[["day"]])
        rmse = np.sqrt(mean_squared_error(test_df["Close"], preds))
        return float(rmse)
    except Exception:
        return np.nan

# ---------------------------------
# ✅ Forecast 30 Days safely
# ---------------------------------
def get_forecast(data: pd.DataFrame, order: int) -> pd.DataFrame:
    """
    Forecast 30 days using Linear Regression. Never throws exceptions.
    """
    if data.empty or "Close" not in data.columns:
        return pd.DataFrame(columns=["Close"])

    try:
        df = data.copy().reset_index()
        df["day"] = np.arange(len(df))

        model = LinearRegression()
        model.fit(df[["day"]], df["Close"])

        future_days = np.arange(len(df), len(df) + 30).reshape(-1, 1)
        preds = model.predict(future_days)

        last_date = df["Date"].iloc[-1]
        if not isinstance(last_date, pd.Timestamp):
            last_date = pd.to_datetime(last_date, errors="coerce")

        if pd.isna(last_date):
            idx = pd.RangeIndex(start=0, stop=30)  # failsafe integer index
        else:
            idx = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=30)

        return pd.DataFrame({"Close": preds}, index=idx)

    except Exception:
        return pd.DataFrame(columns=["Close"])
