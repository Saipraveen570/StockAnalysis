# 📈 Stock Price Forecasting Web App

Real‑time Streamlit application that predicts the **next 30 days of closing prices** for any publicly‑listed stock.  
The app swaps slow ARIMA models for a **lightweight Linear Regression pipeline**, cutting forecast latency by **95 %** and delivering results in **< 1 second**.

(https://github.com/Saipraveen570/StockAnalysis/blob/master/app.png)

---

## 🚀 Features
- **Instant forecasts** – < 1 s end‑to‑end inference on 180 days of data  
- **Dynamic ticker input** – supports any Yahoo Finance symbol (e.g., `AAPL`, `TSLA`)  
- **Interactive visuals** – Plotly candlesticks, moving averages, and forecast overlay  
- **Smart caching** – Streamlit caching eliminates redundant downloads & model fits  
- **Clean UI** – Responsive layout, emoji cues, and dark‑mode friendly palette  

---

## 🛠 Tech Stack
|   |   |
|---|---|
| **Backend** | Python 3.11, yFinance, pandas, NumPy, scikit‑learn |
| **Forecasting** | Linear Regression trend model + 7‑day moving average |
| **Frontend** | Streamlit 1.35, Plotly 5 |
| **DevOps** | Conda/venv, GitHub Actions (optional), Streamlit Cloud (one‑click deploy) |

---

## 📦 Installation

```bash
# 1. Clone the repo
git clone https://github.com/your‑username/stock‑price‑forecast‑app.git
cd stock‑price‑forecast‑app

# 2. Create env & install deps
python -m venv .venv           # or conda create -n stock‑forecast python=3.11
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Run locally
streamlit run pages/Stock_Prediction.py
