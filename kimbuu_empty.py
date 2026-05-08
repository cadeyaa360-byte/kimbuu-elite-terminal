import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import google.generativeai as genai
from PIL import Image

# 1. SETUP & PAGE CONFIG
st.set_page_config(page_title="KIMBUU ELITE", layout="wide")

# Connect to the AI Brain
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("Please add your GEMINI_API_KEY to Streamlit Secrets!")

st.title("🛡️ KIMBUU ELITE: VISION TERMINAL")

# 2. MARKET MATH SECTION
st.header("📈 Live Market Math")
ticker = st.text_input("Enter Ticker (e.g., BTC-USD)", "BTC-USD")

# Fetch 60 days of data
df = yf.download(ticker, period="60d", interval="15m")

if not df.empty:
    # FIX: Flatten the multi-index columns from yfinance
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Ensure we have enough data for EMA 200
    if len(df) > 200:
        # Calculations
        df['EMA_200'] = ta.ema(df['Close'], length=200)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        # Remove empty rows safely
        df = df.dropna(subset=['EMA_200', 'RSI'])
        
        if not df.empty:
            col1, col2, col3 = st.columns(3)
            
            # Get the very last values
            current_price = float(df['Close'].iloc[-1])
            current_rsi = float(df['RSI'].iloc[-1])
            current_ema = float(df['EMA_200'].iloc[-1])

            col1.metric("Price", f"${current_price:,.2f}")
            col2.metric("RSI (14)", round(current_rsi, 2))
            
            if current_price > current_ema:
                col3.success("Trend: BULLISH 📈")
            else:
                col3.error("Trend: BEARISH 📉")
                
            st.line_chart(df[['Close', 'EMA_200']])
    else:
        st.warning("Not enough historical data for this ticker yet. Try BTC-USD.")
else:
    st.info("Searching for ticker data...")

st.divider()

# 3. AI VISION SECTION
st.header("📸 CADE VISION: AI Chart Scanner")
st.write("Upload a chart screenshot for AI analysis.")

uploaded_file = st.file_uploader("Choose a chart image...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Scanning market structure...", use_container_width=True)
    
    with st.spinner("AI Oracle is analyzing patterns..."):
        try:
            prompt = "You are a Master Crypto Trader. Analyze this chart. Identify the trend, support/resistance levels, and give a clear BUY, SELL, or WAIT signal with a detailed reason."
            response = model.generate_content([prompt, img])
            
            st.subheader("🤖 AI Verdict:")
            st.write(response.text)
        except Exception as e:
            st.error(f"AI Scanner error: {e}")
