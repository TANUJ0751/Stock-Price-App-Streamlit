import streamlit as st
import pandas as pd
import yfinance as yf
import cufflinks as cf
import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots


#app title
st.markdown("""
# Stock Price App
Shown are the Stock Price of the selected stock.

**Credits**
-App Built By Tanuj Jain
-Built in `Python` using `Streamlit`,`cufflinks`,`pandas`,`datetime` and `yfinance` libraries.
""")

st.write("--------")
#sidebar
st.sidebar.subheader("Select Stock")
start_date=st.sidebar.date_input("Start Date",datetime.date(2019,1,1))
end_date=st.sidebar.date_input("End Date",datetime.date(2024,12,1))

#Getting Ticker Data
ticker_list=pd.read_csv('stocks.txt')
ticker_Symbol=st.sidebar.selectbox("Stock Ticker",ticker_list)
tickerData=yf.Ticker(ticker_Symbol)
tickerDf=tickerData.history(period="1d",start=start_date,end=end_date)

#Ticker Information
stock_name=tickerData.info['longName']
st.write(f"# {stock_name}")

change=round(tickerData.info['currentPrice']-tickerData.info['previousClose'],2)
changeper=round(change/(tickerData.info['previousClose']/100),2)
if change>0:
    color='green'
elif change<0:
    color='red'
else:
    color='grey'
st.markdown(f"<h2 style='color:{color}'>{tickerData.info['currentPrice']} {tickerData.info['currency']} <h3 style='color:{color}'>{change} {changeper}%</h3></h2>",unsafe_allow_html=True)

company_website = tickerData.info['website']

domain = company_website.split("//")[-1].split("/")[0]  # Extract domain

logo_url = f"https://logo.clearbit.com/{domain}"

st.image(logo_url)

st.write(f"**Sector :** {tickerData.info['sector']}")
stock_summary=tickerData.info['longBusinessSummary']
st.write(stock_summary)
periods=['1d','5d','1mo','2mo']
#candlestick Chart 
if ticker_Symbol:
    if not tickerDf.empty:
        st.write("--------")
        
        cperiod=st.selectbox("Select Date range",periods)
        tickerDf=tickerData.history(period=cperiod,start=start_date,end=end_date)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                    vertical_spacing=0.03, row_heights=[0.7, 0.3],
                    subplot_titles=['Candlestick Chart', 'Volume Chart'],
                    row_titles=['', 'Volume'])
        fig.add_trace(go.Candlestick(
                        x=tickerDf.index,
                        open=tickerDf['Open'],
                        high=tickerDf['High'],
                        low=tickerDf['Low'],
                        close=tickerDf['Close'],
                        name="Candlestick"
                        ), row=1, col=1)
        fig.add_trace(
                go.Bar(
                    x=tickerDf.index,
                    y=tickerDf['Volume'],
                    name='Volume',
                    marker_color='rgba(0, 200, 0, 0.5)'  
                ),
                row=2, col=1  )

        #Chart Layout
        fig.update_layout(
            title=f'{ticker_Symbol} Stock Price and Volume',
            xaxis_title='Date',
            yaxis_title='Price (USD)',
            xaxis_rangeslider_visible=False,  
            height=600  
        )
        #display the chart
        st.plotly_chart(fig,use_container_width=True)
#bollinger band
if not tickerDf.empty:
    st.write("--------")
    bperiod=st.selectbox("Select Date range for Bollinger Bands",periods)
    MA=st.selectbox("Select DMA For Bollinger Bands",[10,20,30,40,50,60])
    tickerDf=tickerData.history(period=bperiod,start=start_date,end=end_date)
    #Moving Average Calculation
    tickerDf[f'{MA}_MA'] = tickerDf['Close'].rolling(window=MA).mean()
    tickerDf['Upper_Band'] = tickerDf[f'{MA}_MA'] + 2 * tickerDf['Close'].rolling(window=MA).std()
    tickerDf['Lower_Band'] = tickerDf[f'{MA}_MA'] - 2 * tickerDf['Close'].rolling(window=MA).std()
    # Plotting Bollinger Bands
    fig2 = go.Figure(data=[
    go.Candlestick(x=tickerDf.index,
                   open=tickerDf['Open'],
                   high=tickerDf['High'],
                   low=tickerDf['Low'],
                   close=tickerDf['Close'],
                   name='Candlestick'),
    go.Scatter(x=tickerDf.index, y=tickerDf['Upper_Band'], mode='lines', name='Upper Bollinger Band'),
    go.Scatter(x=tickerDf.index, y=tickerDf['Lower_Band'], mode='lines', name='Lower Bollinger Band'),
    go.Scatter(x=tickerDf.index, y=tickerDf[f'{MA}_MA'], mode='lines', name=f'{MA} Day Moving Average')
])
    fig2.update_layout(title=f"{ticker_Symbol} Bollinger Band",xaxis_title="Date",yaxis_title="Price",xaxis_rangeslider_visible=False)
    st.plotly_chart(fig2)

st.write(tickerData.info)
st.write(tickerDf)