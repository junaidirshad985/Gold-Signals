
import streamlit as st
import pandas as pd
import requests
import datetime

# Settings
API_KEY = '359659ab-af4e-48e1-bbc9-b7ef4a41a3da'
symbol = 'XAUUSD'

st.set_page_config(page_title="Gold Signals", layout="wide")
st.title("📈 Live XAUUSD Gold Signal System")

# Fetch data
@st.cache_data(ttl=300)
def fetch_data():
    url = f'https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol=XAU&to_symbol=USD&interval=5min&apikey={API_KEY}&outputsize=compact'
    r = requests.get(url)
    data = r.json()
    if 'Time Series FX (5min)' not in data:
        raise ValueError("API Error or Limit Reached")
    df = pd.DataFrame.from_dict(data['Time Series FX (5min)'], orient='index', dtype='float')
    df.columns = ['Open', 'High', 'Low', 'Close']
    df = df.sort_index()
    return df

# Signal logic
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def generate_signal(df):
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    df['EMA200'] = df['Close'].ewm(span=200).mean()
    df['RSI'] = compute_rsi(df['Close'])
    last = df.iloc[-1]
    if last['EMA50'] > last['EMA200'] and last['RSI'] > 55:
        return "📘 BUY", "green"
    elif last['EMA50'] < last['EMA200'] and last['RSI'] < 45:
        return "📕 SELL", "red"
    else:
        return "⚪ NO SIGNAL", "gray"

# Run
try:
    df = fetch_data()
    signal, color = generate_signal(df)
    st.subheader(f"📢 Signal: {signal}")
    st.line_chart(df['Close'])
    st.caption(f"Updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
except Exception as e:
    st.error(f"⚠️ {e}")
