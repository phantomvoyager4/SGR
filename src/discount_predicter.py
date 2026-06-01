import json
import pandas as pd
from prophet import Prophet
import plotly
from prophet.diagnostics import cross_validation, performance_metrics

chunk = 1
product_id = "1200"
history = []

with open(f"data/games_prices/price_data_chunk_{chunk}.jsonl", "r") as file:
    for line in file:
        data = json.loads(line)
        if product_id in data and data[product_id]:
            for entry in data[product_id]:
                for timestamp, price in entry.items():
                    history.append({"ds": timestamp, "y": price})

if not history:
    print(f"No data found for product {product_id} in chunk {chunk}.")
    exit()

for i in range(len(history)):
    date = history[i]['ds']
    date = date[:10]
    history[i]['ds'] = date

df = pd.DataFrame(history)

df['ds'] = pd.to_datetime(df['ds'])

profecy = Prophet()
profecy.fit(df)

today = pd.Timestamp.now().normalize()

future_dates = pd.date_range(start=today, periods=30, freq='D')

future = pd.DataFrame({'ds': future_dates})

future.tail()

prediction = profecy.predict(future)
prediction[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()

original_price = df['y'][0]

results = pd.DataFrame({
    'date': prediction['ds'],
    'price': original_price,
    'predicted_price': round(prediction['yhat'], 0),
    'cut': round(((original_price - prediction['yhat']) / original_price) * 100, 0)
})

# df_cv = cross_validation(
#     profecy, 
#     initial='30 days',
#     period='10 days',
#     horizon='30 days'
# )

# df_p = performance_metrics(df_cv)

print(results)

# print(df_p[['horizon', 'mae', 'mape']].head())