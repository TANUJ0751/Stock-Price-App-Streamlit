from joblib import load
import yfinance as yf
from datetime import datetime
import pandas as pd
current_date = datetime.now().date()

print(current_date)

stock="DOV"
model_dir=f"./models/{stock}/"
# Load saved model and scaler
scaler1 = load(f'{model_dir}{stock}_scaler.joblib')
model1 = load(f'{model_dir}{stock}_predictor.joblib')
data=yf.Ticker(stock)
SmaEma=data.history(period="2y")
data=data.info
open_close=data['open']-data['currentPrice']
high_low=data['dayHigh']-data['dayLow']
volume=data['volume']
quarter_end= 1 if current_date.month % 3 == 0 else 0
current_date=datetime.today().date()
today_data = pd.DataFrame({
    'Open': data['open'],
    'High': data['dayHigh'],
    'Low': data['dayLow'],
    'Close': data['currentPrice'],
    'Volume': data['volume']
}, index=[current_date])  # Ensure the index matches `ticker.history`


SmaEma=pd.concat([SmaEma,today_data])
print(SmaEma.tail())

sma10=SmaEma['Close'].rolling(window=10).mean()[-1]
sma50=SmaEma['Close'].rolling(window=50).mean()[-1]
sma200=SmaEma['Close'].rolling(window=200).mean()[-1]
ema10=SmaEma['Close'].ewm(span=10,adjust=False).mean()[-1]
ema50=SmaEma['Close'].ewm(span=50,adjust=False).mean()[-1]
ema200=SmaEma['Close'].ewm(span=200,adjust=False).mean()[-1]
print(sma10,sma50,sma200,ema10,ema50,ema200)


# Example new data
new_data = [[open_close, high_low, volume, quarter_end,sma10,sma50,sma200,ema10,ema50,ema200]]  # Replace with actual feature values
new_data_scaled = scaler1.transform(new_data)
prediction = model1.predict(new_data_scaled)
probability = model1.predict_proba(new_data_scaled)

print("Prediction:", "Bullish" if prediction[0] == 1 else "Bearish")
print("Probability of Price Change:", round(probability[0][1]*100,2),"%")