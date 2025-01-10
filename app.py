import streamlit as st
import pandas as pd
import yfinance as yf
import cufflinks as cf
import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from joblib import load
import time

# App Title
st.markdown("""
# Stock Price App
Shown are the Stock Price of the selected stock.

**Credits**
- App Built By Tanuj Jain  
- Built in `Python` using `Streamlit`, `cufflinks`, `pandas`, `datetime`, `plotly`, and `yfinance` libraries.
""")

st.write("--------")

# Sidebar
st.sidebar.subheader("Select Stock")
start_date = st.sidebar.date_input("Start Date", datetime.date(2019, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.date(2024, 12, 1))

# Getting Ticker Data
ticker_list = pd.read_csv('NSE.csv')
ticker_list_LSE = pd.read_csv('LSE.csv')
tickerlist2 = pd.read_csv('nasdaq-listed.csv')

Market = st.sidebar.selectbox("Select Market", ["NSE", "NASDAQ", "LSE"])
if Market == "NSE":
    ticker_Symbol = st.sidebar.selectbox("Stock Symbol", ticker_list['SYMBOL'])
    ticker_Symbol = ticker_Symbol + ".NS"
elif Market == "LSE":
    ticker_Symbol = st.sidebar.selectbox("Stock Symbol", ticker_list_LSE['Symbol'])
    ticker_Symbol = ticker_Symbol + ".L"
else:
    ticker_Symbol = st.sidebar.selectbox("Stock Symbol", tickerlist2)

tickerData = yf.Ticker(f"{ticker_Symbol}")

# Periodically Refresh Data
refresh_interval = 5  # Refresh every 5 seconds
last_update_time = st.session_state.get('last_update_time', None)

if last_update_time is None or (time.time() - last_update_time > refresh_interval):
    # Update stock data
    tickerDf = tickerData.history(period="1d", start=start_date, end=end_date)
    st.session_state['last_update_time'] = time.time()

# Display Stock Information
if ticker_Symbol:
    stock_name = tickerData.info['longName']
    st.write(f"# {stock_name}")

    current_price = tickerData.info['currentPrice']
    previous_close = tickerData.info['previousClose']
    change = round(current_price - previous_close, 2)
    changeper = round(change / (previous_close / 100), 2)

    color = 'green' if change > 0 else 'red' if change < 0 else 'grey'
    st.markdown(f"<h2 style='color:{color}'>{current_price} {tickerData.info['currency']} <h3 style='color:{color}'>{change} {changeper}%</h3></h2>", unsafe_allow_html=True)

    company_website = tickerData.info.get('website', None)
    if company_website:
        domain = company_website.split("//")[-1].split("/")[0]
        logo_url = f"https://logo.clearbit.com/{domain}"
        st.image(logo_url)

    st.write(f"**Sector :** {tickerData.info.get('sector', 'N/A')}")
    st.write("Fundamentals :")
    st.write(f"**Market Cap :** {tickerData.info.get('marketCap', 'N/A')} {tickerData.info.get('currency', 'N/A')}")
    st.write(f"**Enterprise Value :** {tickerData.info.get('enterpriseValue', 'N/A')} {tickerData.info.get('currency', 'N/A')}")
    st.write(f"**Float Shares :** {tickerData.info.get('floatShares', 'N/A')}")

    # Candlestick Chart
    if not tickerDf.empty:
        st.write("--------")
        periods = ['1d', '5d', '1mo', '2mo']
        cperiod = st.selectbox("Select Date range", periods)
        tickerDf = tickerData.history(period=cperiod, start=start_date, end=end_date)
        
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, 
                            row_heights=[0.7, 0.3], subplot_titles=['Candlestick Chart', 'Volume Chart'])
        fig.add_trace(go.Candlestick(
            x=tickerDf.index,
            open=tickerDf['Open'],
            high=tickerDf['High'],
            low=tickerDf['Low'],
            close=tickerDf['Close'],
            name="Candlestick"
        ), row=1, col=1)
        fig.add_trace(go.Bar(
            x=tickerDf.index,
            y=tickerDf['Volume'],
            name='Volume',
            marker_color='rgba(0, 200, 0, 0.5)'
        ), row=2, col=1)
        fig.update_layout(title=f'{ticker_Symbol} Stock Price and Volume',
                          height=600)
        st.plotly_chart(fig, use_container_width=True)
