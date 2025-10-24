import streamlit as st
import pandas as pd
import time
from pages.utils.model_train import (
    get_data,
    get_rolling_mean,
    get_differencing_order,
    scaling,
    evaluate_model,
    get_forecast,
    inverse_scaling,
)
from pages.utils.plotly_figure import plotly_table, Moving_average_forecast

# ------------------------ PAGE CONFIG ------------------------
st.set_page_config(
    page_title="Stock Prediction",
    page_icon="📈",
    layout="wide",
)

st.title("🔮 Stock Price Prediction Dashboard")

# ------------------------ INPUT SECTION ------------------------
col1, col2 = st.columns([2, 1])
with col1:
    ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, TSLA, INFY):", "AAPL").upper()
with col2:
    if st.button("Predict"):
        st.session_state["run_prediction"] = True
    else:
        st.session_state["run_prediction"] = st.session_state.get("run_prediction", False)

# ------------------------ APP START ------------------------
if st.session_state["run_prediction"]:
    try:
        with st.spinner("📡 Fetching stock data..."):
            close_price = get_data(ticker)
            time.sleep(0.5)

        st.subheader(f"🔍 Predicting Next 30 Days Close Price for: **{ticker}**")

        with st.spinner("⚙️ Preparing data..."):
            rolling_price = get_rolling_mean(close_price)
            differencing_order = get_differencing_order(rolling_price)
            scaled_data, scaler = scaling(rolling_price)
            time.sleep(0.5)

        with st.spinner("🧠 Evaluating model..."):
            rmse = evaluate_model(scaled_data, differencing_order)
            st.success(f"✅ Model RMSE Score: **{rmse:.3f}**")

        with st.spinner("📊 Generating forecast..."):
            forecast = get_forecast(scaled_data, differencing_order)
            forecast["Close"] = inverse_scaling(scaler, forecast["Close"])

        # ------------------------ DISPLAY FORECAST TABLE ------------------------
        st.write("### 📅 Forecast Data (Next 30 Days)")
        fig_tail = plotly_table(forecast.sort_index(ascending=True).round(3))
        fig_tail.update_layout(height=250)
        st.plotly_chart(fig_tail, use_container_width=True)

        # ------------------------ VISUALIZATION ------------------------
        st.markdown("""<hr style="height:2px;border:none;color:#0078ff;background-color:#0078ff;" /> """,
                    unsafe_allow_html=True)

        st.write("### 📈 Forecast Visualization")
        combined_forecast = pd.concat([rolling_price, forecast])
        st.plotly_chart(Moving_average_forecast(combined_forecast.iloc[-200:]),
                        use_container_width=True)

        st.balloons()

    except Exception as e:
        st.error(f"⚠️ Something went wrong: {str(e)}. Please verify the ticker symbol and try again.")

else:
    st.info("👆 Enter a valid stock ticker above and click **Predict** to start forecasting.")
