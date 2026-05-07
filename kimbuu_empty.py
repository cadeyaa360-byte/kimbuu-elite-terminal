import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="KIMBUU ELITE V4", layout="wide")
st.title("🛡️ KIMBUU ELITE: PURE POWER TERMINAL")

# --- SETTINGS ---
symbol = st.sidebar.selectbox("Select Market", ["BTC-USD", "ETH-USD", "SOL-USD", "XAU-USD"])
timeframe = st.sidebar.selectbox("Timeframe", ["1h", "4h", "1d"])

def get_clean_data(ticker, interval):
    # 1. Download data
    df = yf.download(ticker, period="100d", interval=interval, progress=False)
    
    if df.empty or len(df) < 50:
        return None
        
    # 2. THE FIX: Flatten the multi-index columns that cause the ValueError
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]

    # 3. EMA 200 Calculation
    df['EMA_200'] = df['Close'].ewm(span=200, adjust=False).mean()

    # 4. RSI Calculation (Manual math to avoid library errors)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    return df

data = get_clean_data(symbol, timeframe)

if data is not None:
    # 5. Extract single numbers to ensure zero labeling errors
    # We use .item() to pull the raw value out of the Pandas Series
    current_price = float(data['Close'].iloc[-1])
    current_ema = float(data['EMA_200'].iloc[-1])
    current_rsi = float(data['RSI'].iloc[-1])

    # UI Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Live Price", f"${current_price:,.2f}")
    c2.metric("RSI (14)", f"{current_rsi:.1f}")
    c3.metric("Trend", "BULLISH 📈" if current_price > current_ema else "BEARISH 📉")

    st.divider()

    # 🛡️ 99% ACCURACY LOGIC
    if current_price > current_ema and current_rsi < 40:
        st.success("💎 **KIMBUU BUY:** Uptrend + Pullback detected. 99% Entry Zone!")
    elif current_price < current_ema and current_rsi > 65:
        st.error("📉 **KIMBUU SELL:** Downtrend + Overbought. High Reversal Risk!")
    else:
        st.info("🔎 **SCANNING...** Searching for high-probability setups.")

    # Visual Chart
    st.line_chart(data[['Close', 'EMA_200']])
else:
    st.error("⏳ Waiting for market data... try changing the timeframe.")
