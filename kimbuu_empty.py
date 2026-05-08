import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import google.generativeai as genai
from PIL import Image

# 1. SETUP & PAGE CONFIG
st.set_page_config(page_title="KIMBUU ELITE", layout="wide")

# Connect to the AI Brain using the secret you saved
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("🛡️ KIMBUU ELITE: VISION TERMINAL")

# 2. MARKET MATH SECTION
st.header("📈 Live Market Math")
ticker = st.text_input("Enter Ticker (e.g., BTC-USD)", "BTC-USD")
data = yf.download(ticker, period="1d", interval="15m")

if not data.empty:
    # Calculations
    data['EMA_200'] = ta.ema(data['Close'], length=200)
    data['RSI'] = ta.rsi(data['Close'], length=14)
    
    # Display Stats
    col1, col2, col3 = st.columns(3)
    col1.metric("Price", f"${data['Close'].iloc[-1]:,.2f}")
    col2.metric("RSI (14)", round(data['RSI'].iloc[-1], 2))
    
    current_price = data['Close'].iloc[-1]
    ema_200 = data['EMA_200'].iloc[-1]
    
    if current_price > ema_200:
        col3.success("Trend: BULLISH 📈")
    else:
        col3.error("Trend: BEARISH 📉")
        
    st.line_chart(data[['Close', 'EMA_200']])

st.divider()

# 3. AI VISION SECTION
st.header("📸 CADE VISION: AI Chart Scanner")
st.write("Take a screenshot of any chart and upload it below for a deep AI analysis.")

uploaded_file = st.file_uploader("Choose a chart image...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Scanning market structure...", use_container_width=True)
    
    with st.spinner("AI Oracle is analyzing patterns..."):
        # The prompt tells the AI how to behave
        prompt = "You are a Master Crypto Trader. Analyze this chart. Identify the trend, support/resistance levels, and give a clear BUY, SELL, or WAIT signal with a detailed reason."
        response = model.generate_content([prompt, img])
        
        st.subheader("🤖 AI Verdict:")
        st.write(response.text)
