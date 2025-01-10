import streamlit as st
import pandas as pd
import yfinance as yf
import cufflinks as cf
import datetime 
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from joblib import load
import time


#app title
st.markdown("""
# Stock Price App
Shown are the Stock Price of the selected stock.

**Credits**
-App Built By Tanuj Jain \n
-Built in `Python` using `Streamlit`,`cufflinks`,`pandas`,`datetime`,`plotly` and `yfinance` libraries.
""")

st.write("--------")
#sidebar
st.sidebar.subheader("Select Stock")
start_date=st.sidebar.date_input("Start Date",datetime.date(2019,1,1))
end_date=st.sidebar.date_input("End Date",datetime.date(2024,12,1))

#Getting Ticker Data
ticker_list=pd.read_csv('NSE.csv')
ticker_list_LSE=pd.read_csv('LSE.csv')
tickerlist2=pd.read_csv('nasdaq-listed.csv')
Market=st.sidebar.selectbox("Select Market",["NSE","NASDAQ","LSE"])
if Market=="NSE":
    ticker_Symbol=st.sidebar.selectbox("Stock Symbol",ticker_list['SYMBOL'])
    ticker_Symbol=ticker_Symbol+".NS"
elif Market=="LSE":
    ticker_Symbol=st.sidebar.selectbox("Stock Symbol",ticker_list_LSE['Symbol'])
    ticker_Symbol=ticker_Symbol+".L"

    #ticker_Symbol=st.sidebar.selectbox("Stock Symbol",crypto_list["CODE"])

    #tickerData=yf.Ticker(f"{ticker_Symbol}-USD")
else:
    ticker_Symbol=st.sidebar.selectbox("Stock Symbol",tickerlist2)
    
tickerData=yf.Ticker(f"{ticker_Symbol}")
tickerDf=tickerData.history(period="1d",start=start_date,end=end_date)
#Prediction
data=tickerData.info
if Market=="NSE" or Market=="NASDAQ":
    if st.sidebar.button("Predict Stock"):
        stock=ticker_Symbol
        if Market=="NASDAQ":
            model_dir=f"./models/{stock}/"
            scaler1 = load(f'{model_dir}{stock}_scaler.joblib')
            model1 = load(f'{model_dir}{stock}_predictor.joblib')
        else:
            model_dir=f"./modelsNS/{stock}.NS/"
            scaler1 = load(f'{model_dir}{stock}.NS_scaler.joblib')
            model1 = load(f'{model_dir}{stock}.NS_predictor.joblib')
        current_date = datetime.datetime.now()
        # Load saved model and scaler
        
        Yf_data=yf.Ticker(stock)
        SmaEma=tickerData.history(period="max")
        
        open_close=data['open']-data['currentPrice']
        high_low=data['dayHigh']-data['dayLow']
        volume=data['volume']
        quarter_end= 1 if current_date.month % 3 == 0 else 0
        current_date=datetime.datetime.today().date()
        today_data = pd.DataFrame({
            'Open': data['open'],
            'High': data['dayHigh'],
            'Low': data['dayLow'],
            'Close': data['currentPrice'],
            'Volume': data['volume']
        }, index=[current_date])  # Ensure the index matches `ticker.history`


        SmaEma=pd.concat([SmaEma,today_data])
        # st.sidebar.write(SmaEma.tail())

        sma10=SmaEma['Close'].rolling(window=10).mean()[-1]
        sma50=SmaEma['Close'].rolling(window=50).mean()[-1]
        sma200=SmaEma['Close'].rolling(window=200).mean()[-1]
        ema10=SmaEma['Close'].ewm(span=10,adjust=False).mean()[-1]
        ema50=SmaEma['Close'].ewm(span=50,adjust=False).mean()[-1]
        ema200=SmaEma['Close'].ewm(span=200,adjust=False).mean()[-1]
        print(open_close, high_low, volume, quarter_end,sma10,sma50,sma200,ema10,ema50,ema200)
        new_data = [[open_close, high_low, volume, quarter_end,sma10,sma50,sma200,ema10,ema50,ema200]]  # Replace with actual feature values
        new_data_scaled = scaler1.transform(new_data)
        
        prediction = model1.predict(new_data_scaled)
        probability = model1.predict_proba(new_data_scaled)
        if prediction[0] == 1 :
            color="green"
            st.sidebar.markdown(f"<h2 style='color:{color}'>Bullish<br>Probability of Bullish: {round(probability[0][1]*100,2)}%</h2>",unsafe_allow_html=True)
            
        else:
            color='red'
            st.sidebar.markdown(f"<h2 style='color:{color}'>Bearish<br> Probability of Bearish: {round(probability[0][1]*100,2)}%</h3>",unsafe_allow_html=True)
            
if ticker_Symbol:

    while True:
        tickerData=yf.Ticker(f"{ticker_Symbol}")
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
        if st.pills("",options="View Long Summary"):
            st.write(tickerData.info['longBusinessSummary'])
        st.write("Fundamentals :")
        st.write(f"**Market Cap :** {tickerData.info['marketCap']} {tickerData.info['currency']}")
        st.write(f"**Enterprise Value :** {tickerData.info['enterpriseValue']} {tickerData.info['currency']}")
        st.write(f"**Float Shares :** {tickerData.info['floatShares']}")


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
                    dragmode="zoom",
                    xaxis=dict(
                    rangeslider=dict(visible=True),  # Enable the range slider for scrolling
                    type="date"),
                    yaxis=dict(
                    fixedrange=False  ),
                    title=f'{ticker_Symbol} Stock Price and Volume',
                    legend=dict(
                    orientation="h",  # Horizontal orientation
                    yanchor="top",
                    y=-0.2,  # Move legend below the chart
                    xanchor="center",
                    x=0.5),
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
            fig2.update_layout(title=f"{ticker_Symbol} Bollinger Band",
                dragmode="zoom",
                xaxis=dict(
                rangeslider=dict(visible=True),  # Enable the range slider for scrolling
                type="date"),
                yaxis=dict(
                fixedrange=False),
                legend=dict(
                orientation="h",  # Horizontal orientation
                yanchor="top",
                y=-0.2,  # Move legend below the chart
                xanchor="center",
                x=0.5
            ),xaxis_title="Date",yaxis_title="Price",xaxis_rangeslider_visible=False)
            st.plotly_chart(fig2)
        time.sleep(3)
        st.experimental_rerun()
        #st.write(tickerData.info)
        #st.write(tickerDf)