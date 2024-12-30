import yfinance as yf
ticker_symbol="ACONW"
try:
        # Try to fetch data with period 'max'
        data = yf.Ticker(ticker_symbol).history(period="max")
        print(f"Data for {ticker_symbol} with period 'max':")
        print(data)
except ValueError as e:
    # If 'max' is invalid, fallback to '1d'
    
    data = None
print(data.empty)