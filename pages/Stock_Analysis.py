import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import datetime as dt


def fetch_stock_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetch historical stock data using yfinance.
    """
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        if data.empty:
            raise ValueError("No data found for the given ticker or date range.")
        data.dropna(inplace=True)
        return data
    except Exception as e:
        raise RuntimeError(f"Error fetching data: {e}")


def calculate_moving_averages(data: pd.DataFrame, short_window=20, long_window=50) -> pd.DataFrame:
    """
    Add short-term and long-term moving averages to the DataFrame.
    """
    data['Short_MA'] = data['Close'].rolling(window=short_window).mean()
    data['Long_MA'] = data['Close'].rolling(window=long_window).mean()
    return data


def calculate_RSI(data: pd.DataFrame, period=14) -> pd.DataFrame:
    """
    Calculate the Relative Strength Index (RSI).
    """
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    return data


def plot_stock_data(data: pd.DataFrame, ticker: str):
    """
    Plot stock closing price, moving averages, and RSI.
    """
    plt.figure(figsize=(12, 8))

    # --- Price + MA Plot ---
    plt.subplot(2, 1, 1)
    plt.plot(data.index, data['Close'], label=f'{ticker} Close', linewidth=1.5)
    plt.plot(data.index, data['Short_MA'], label='20-Day MA', linestyle='--')
    plt.plot(data.index, data['Long_MA'], label='50-Day MA', linestyle='-.')
    plt.title(f"{ticker} Price Trend & Moving Averages")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)

    # --- RSI Plot ---
    plt.subplot(2, 1, 2)
    plt.plot(data.index, data['RSI'], color='purple', label='RSI (14)')
    plt.axhline(70, color='r', linestyle='--', alpha=0.7)
    plt.axhline(30, color='g', linestyle='--', alpha=0.7)
    plt.title("Relative Strength Index (RSI)")
    plt.xlabel("Date")
    plt.ylabel("RSI")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    plt.show()


def plot_volume(data: pd.DataFrame, ticker: str):
    """
    Plot trading volume over time.
    """
    plt.figure(figsize=(10, 4))
    plt.bar(data.index, data['Volume'], color='gray', alpha=0.5)
    plt.title(f"{ticker} Trading Volume")
    plt.xlabel("Date")
    plt.ylabel("Volume")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()


def generate_summary(data: pd.DataFrame, ticker: str):
    """
    Display summary statistics and latest trend information.
    """
    latest_close = data['Close'].iloc[-1]
    avg_volume = data['Volume'].mean()
    price_change = data['Close'].pct_change().mean() * 100

    print("\n--- Stock Summary Report ---")
    print(f"Ticker: {ticker}")
    print(f"Latest Closing Price: ${latest_close:.2f}")
    print(f"Average Daily Volume: {avg_volume:,.0f}")
    print(f"Average Daily % Change: {price_change:.2f}%")

    if data['RSI'].iloc[-1] > 70:
        print("RSI indicates: ⚠️ Overbought")
    elif data['RSI'].iloc[-1] < 30:
        print("RSI indicates: 💡 Oversold")
    else:
        print("RSI indicates: ✅ Neutral trend")


def main():
    print("\n📊 Welcome to Stock Analysis Tool")
    ticker = input("Enter Stock Ticker (e.g., AAPL, TSLA, INFY.NS): ").upper().strip()
    start_date = input("Enter Start Date (YYYY-MM-DD): ").strip()
    end_date = input("Enter End Date (YYYY-MM-DD): ").strip()

    if not ticker:
        print("Ticker cannot be empty.")
        return

    try:
        data = fetch_stock_data(ticker, start_date, end_date)
        data = calculate_moving_averages(data)
        data = calculate_RSI(data)
        generate_summary(data, ticker)
        plot_stock_data(data, ticker)
        plot_volume(data, ticker)

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
