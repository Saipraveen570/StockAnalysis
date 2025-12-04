import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
from datetime import datetime, timedelta, date
import sys
import os
import plotly.graph_objects as go

# Fix import path for utils (for Streamlit Cloud / different layout)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# If you have the helper plotting functions, import them. If not, we'll fall back to simple plotting below.
try:
    from pages.utils.plotly_figure import candlestick, RSI, Moving_average, MACD  # type: ignore
    HAS_UTILS = True
except Exception:
    HAS_UTILS = False

# ------------------- PAGE CONFIG -------------------
st.set_page_config(page_title="🤖 Stock Price Prediction", layout="wide")
st.title("🤖 Stock Price Prediction Dashboard")
st.markdown(
    "Predict short-term stock prices with simple ML models. Uses Yahoo Finance primarily and Alpha Vantage (compact) as a fallback."
)

# ------------------- USER INPUT -------------------
ticker = st.text_input("Enter Stock Symbol (e.g. AAPL, TSLA, INFY.NS)", "AAPL").upper()
col1, col2, col3 = st.columns(3)
with col1:
    start_date = st.date_input("Start Date", datetime(2024, 1, 1).date())
with col2:
    end_date = st.date_input("End Date", datetime.today().date())
with col3:
    future_horizon = st.slider("Forecast horizon (days)", 7, 90, 30, step=1)

if start_date > end_date:
    st.error("Start Date must be before End Date.")
    st.stop()

# ------------------- DATA FETCHING -------------------
st.info("⏳ Fetching data from Yahoo Finance...")

@st.cache_data(ttl=600)
def fetch_yahoo(ticker: str, start_dt: date, end_dt: date) -> pd.DataFrame:
    """
    Fetch from Yahoo using yfinance. Make end_date inclusive by adding one day to the end param.
    """
    try:
        df = yf.download(ticker, start=start_dt, end=end_dt + timedelta(days=1), progress=False)
        if df.empty:
            return pd.DataFrame()
        df.index = pd.to_datetime(df.index)
        return df
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def fetch_alpha(ticker: str, start_dt: date, end_dt: date) -> pd.DataFrame:
    """
    Fallback using Alpha Vantage free tier (compact). compact returns approx last 100 daily rows.
    We'll filter for requested range; if filtered is empty we still return compact data (recent history).
    """
    try:
        try:
            ALPHA_KEY = st.secrets["general"]["ALPHA_VANTAGE_KEY"]
        except Exception:
            st.error("Alpha Vantage API key not found in st.secrets['general']['ALPHA_VANTAGE_KEY'].")
            return pd.DataFrame()

        ts = TimeSeries(key=ALPHA_KEY, output_format="pandas")
        data, _ = ts.get_daily(symbol=ticker, outputsize="compact")  # compact for free tier

        data = data.rename(
            columns={
                "1. open": "Open",
                "2. high": "High",
                "3. low": "Low",
                "4. close": "Close",
                "5. volume": "Volume",
            }
        )
        data.index = pd.to_datetime(data.index)
        data.sort_index(inplace=True)

        if "Adj Close" not in data.columns and "Close" in data.columns:
            data["Adj Close"] = data["Close"]

        filtered = data.loc[(data.index.date >= start_dt) & (data.index.date <= end_dt)]
        return filtered if not filtered.empty else data

    except Exception as e:
        st.error(f"Alpha Vantage failed: {e}")
        return pd.DataFrame()

# Try Yahoo first
data = fetch_yahoo(ticker, start_date, end_date)

# Fallback to Alpha if Yahoo returned nothing
if data.empty:
    st.warning("⚠️ Yahoo Finance returned no data. Trying Alpha Vantage (compact — last ~100 days)...")
    data = fetch_alpha(ticker, start_date, end_date)

if data.empty:
    st.error(f"❌ Could not fetch data for {ticker}. Check symbol or API key.")
    st.stop()

# If Alpha provided only recent data and it doesn't cover requested start_date, warn user
try:
    min_date = data.index.date.min()
    if min_date > start_date:
        st.warning(
            f"Note: available data starts on {min_date}. Alpha Vantage (compact) returns only ~100 most recent daily rows on free tier."
        )
except Exception:
    pass

# ------------------- CLEAN & PREP -------------------
# Ensure numeric columns and drop rows with missing Close
for col in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]:
    if col in data.columns:
        data[col] = pd.to_numeric(data[col], errors="coerce")

data = data.dropna(subset=["Close"])
if data.empty:
    st.error("No valid 'Close' prices available after cleaning.")
    st.stop()

# Filter again to requested date range (in case fallback returned extra)
data = data.loc[(data.index.date >= start_date) & (data.index.date <= end_date)]
if data.empty:
    st.error("No data for selected date range after filtering.")
    st.stop()

# Expose data range
st.success(f"✅ Data fetched for {ticker} — {data.index.date.min()} to {data.index.date.max()}")

# ------------------- TECHNICAL CHARTS -------------------
st.subheader("📊 Technical Analysis Charts")
if HAS_UTILS:
    try:
        st.plotly_chart(candlestick(data), use_container_width=True)
        st.plotly_chart(RSI(data), use_container_width=True)
        st.plotly_chart(Moving_average(data), use_container_width=True)
        st.plotly_chart(MACD(data), use_container_width=True)
    except Exception as e:
        st.warning(f"Could not render all utils plots: {e}")
        HAS_UTILS = False

if not HAS_UTILS:
    # Minimal fallback charts using Plotly
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=data.index, open=data["Open"], high=data["High"], low=data["Low"], close=data["Close"], name="Price"))
    fig.update_layout(title=f"{ticker} Price Candlestick", xaxis_title="Date", yaxis_title="Price")
    st.plotly_chart(fig, use_container_width=True)

    # RSI fallback
    delta = data["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=data.index, y=rsi, name="RSI"))
    fig_rsi.add_hline(y=70, line_dash="dash")
    fig_rsi.add_hline(y=30, line_dash="dash")
    fig_rsi.update_layout(title="RSI (14)")
    st.plotly_chart(fig_rsi, use_container_width=True)

# ------------------- FEATURE ENGINEERING -------------------
st.subheader("🔧 Feature Engineering")
df = data.copy().sort_index()
df = df.reset_index().rename(columns={df.columns[0]: "Date"})
df["Date"] = pd.to_datetime(df["Date"]).dt.date  # keep date (not datetime) for clarity
df["Close"] = pd.to_numeric(df["Close"], errors="coerce")

# Create lag features and rolling stats
N_LAGS = 5
for lag in range(1, N_LAGS + 1):
    df[f"lag_{lag}"] = df["Close"].shift(lag)

df["roll_mean_7"] = df["Close"].rolling(window=7, min_periods=1).mean().shift(1)
df["roll_std_7"] = df["Close"].rolling(window=7, min_periods=1).std().shift(1).fillna(0)

# Drop rows with NaNs introduced by lags
df = df.dropna(subset=[f"lag_{N_LAGS}"]).reset_index(drop=True)
st.write(f"Features created: lags 1..{N_LAGS}, roll_mean_7, roll_std_7. Data rows available for modeling: {len(df)}")

# ------------------- MODEL SELECTION & TRAIN/TEST -------------------
st.subheader("📈 Model Selection & Forecasting")

feature_cols = [f"lag_{i}" for i in range(1, N_LAGS + 1)] + ["roll_mean_7", "roll_std_7"]

# Time-series train/test split: first 80% train, last 20% test
split_pct = 0.8
split_idx = int(len(df) * split_pct)
train_df = df.iloc[:split_idx].copy()
test_df = df.iloc[split_idx:].copy()

MIN_ROWS_TO_TRAIN = 30
if train_df.shape[0] < MIN_ROWS_TO_TRAIN:
    st.error(f"Not enough training rows (need >= {MIN_ROWS_TO_TRAIN}). Please extend start date or choose a longer range.")
    st.stop()

X_train = train_df[feature_cols].values
y_train = train_df["Close"].values
X_test = test_df[feature_cols].values
y_test = test_df["Close"].values

model_choice = st.selectbox("Choose model", ["Linear Regression", "Random Forest", "Gradient Boosting"])
if model_choice == "Linear Regression":
    model = LinearRegression()
elif model_choice == "Random Forest":
    model = RandomForestRegressor(n_estimators=150, random_state=42)
else:
    model = GradientBoostingRegressor(n_estimators=150, random_state=42)

# Train
with st.spinner("Training model..."):
    model.fit(X_train, y_train)

# Predict
train_pred = model.predict(X_train)
test_pred = model.predict(X_test)

# Metrics
rmse = mean_squared_error(y_test, test_pred, squared=False)
mae = mean_absolute_error(y_test, test_pred)

col_rmse, col_mae = st.columns(2)
col_rmse.metric("Test RMSE", f"{rmse:.4f}")
col_mae.metric("Test MAE", f"{mae:.4f}")

# Plot actual vs predicted
fig = go.Figure()
fig.add_trace(go.Scatter(x=train_df["Date"], y=train_df["Close"], name="Train Actual", line=dict(color="blue")))
fig.add_trace(go.Scatter(x=train_df["Date"], y=train_pred, name="Train Pred", line=dict(color="lightblue", dash="dot")))
fig.add_trace(go.Scatter(x=test_df["Date"], y=test_df["Close"], name="Test Actual", line=dict(color="black")))
fig.add_trace(go.Scatter(x=test_df["Date"], y=test_pred, name="Test Pred", line=dict(color="red", dash="dash")))
fig.update_layout(title=f"{model_choice} — Actual vs Predicted (Test RMSE={rmse:.3f})", xaxis_title="Date", yaxis_title="Price")
st.plotly_chart(fig, use_container_width=True)

# ------------------- RECURSIVE FUTURE FORECAST -------------------
st.subheader(f"🔮 {future_horizon}-Day Recursive Forecast")

# We'll perform a recursive forecast using the latest available features.
last_window = df.copy().reset_index(drop=True)
# Get the last available row to seed recursion
seed_row = last_window.iloc[-1:].copy()
# Build initial feature vector from last row
current_features = seed_row[feature_cols].iloc[0].values.reshape(1, -1)

future_dates = []
future_preds = []
# To compute rolling stats we maintain a list of recent close values (last 7)
recent_closes = list(last_window["Close"].values[-7:])  # may be <7 if small data

for i in range(future_horizon):
    pred = model.predict(current_features)[0]
    future_preds.append(pred)
    next_date = pd.to_datetime(seed_row["Date"].iloc[0]) + pd.Timedelta(days=i + 1)
    future_dates.append(next_date.date())

    # update recent_closes with predicted value
    recent_closes.append(pred)
    if len(recent_closes) > 7:
        recent_closes = recent_closes[-7:]

    # create next feature vector: shift lags, insert pred as lag_1
    prev_lags = list(current_features[0][:N_LAGS])
    # shift: new lag_1 is pred, lag_2 was previous lag_1, ...
    new_lags = [pred] + prev_lags[:-1]
    roll_mean_7 = np.mean(recent_closes)
    roll_std_7 = np.std(recent_closes)
    new_feat = new_lags + [roll_mean_7, roll_std_7]
    current_features = np.array(new_feat).reshape(1, -1)

forecast_df = pd.DataFrame({"Date": future_dates, "Predicted": future_preds})
forecast_df = forecast_df.set_index("Date")

# Plot forecast
st.line_chart(forecast_df)

# ------------------- DOWNLOADS -------------------
st.markdown("### 💾 Download data")
hist_csv = data.reset_index().rename(columns={data.reset_index().columns[0]: "Date"}).to_csv(index=False)
st.download_button(label="Download Historical CSV", data=hist_csv, file_name=f"{ticker}_historical_{start_date}_{end_date}.csv", mime="text/csv")

forecast_csv = forecast_df.reset_index().to_csv(index=False)
st.download_button(label="Download Forecast CSV", data=forecast_csv, file_name=f"{ticker}_forecast_{future_horizon}d.csv", mime="text/csv")

st.success("✅ Forecast complete! Use the model selector to compare models and the horizon slider to adjust prediction length.")
