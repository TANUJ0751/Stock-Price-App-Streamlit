import yfinance as yf

tickerdata=yf.Ticker("BTC-ETH")
data=tickerdata.info
print(data)