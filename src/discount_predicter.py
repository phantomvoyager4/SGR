import json
import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

chunk = 1
product_id = "1670"
history = []

with open(f"data/games_prices/price_data_chunk_{chunk}.jsonl", "r") as file:
    for line in file:
        data = json.loads(line)
        if product_id in data and data[product_id]:
            for entry in data[product_id]:
                for timestamp, price in entry.items():
                    history.append({"ds": timestamp[:10], "y": price})

if not history:
    print(f"No data found for product {product_id} in chunk {chunk}.")
    exit()

df = pd.DataFrame(history)
df['ds'] = pd.to_datetime(df['ds'])
df = df.drop_duplicates(subset=['ds']).sort_values('ds')

df.set_index('ds', inplace=True)
df = df.resample('D').ffill() 
df.reset_index(inplace=True)

df = df.dropna()
df = df.sort_values('ds')

original_price = df['y'].max()

df['month'] = df['ds'].dt.month
df['day_of_week'] = df['ds'].dt.dayofweek
df['day_of_month'] = df['ds'].dt.day
df['quarter'] = df['ds'].dt.quarter
df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)

df['sin_month'] = np.sin(2 * np.pi * df['month'] / 12)
df['cos_month'] = np.cos(2 * np.pi * df['month'] / 12)

is_sale = (df['y'] < original_price).astype(int)
df['days_since_last_sale'] = is_sale.groupby((is_sale != is_sale.shift()).cumsum()).cumcount()

df['days_since_last_sale'] = df['days_since_last_sale'].shift(1).fillna(0)

feature_cols = ['month', 'day_of_week', 'day_of_month', 'quarter', 'is_weekend', 'sin_month', 'cos_month']
X = df[feature_cols]
y = df['y']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, shuffle=False)

train_dataset = lgb.Dataset(X_train, label=y_train)
test_dataset = lgb.Dataset(X_test, label=y_test, reference=train_dataset)

params = {
    'objective': 'regression',
    'metric': 'mae',          
    'boosting_type': 'gbdt',
    'learning_rate': 0.1,    
    'num_leaves': 15,          
    'min_data_in_leaf': 10,    
    'feature_fraction': 0.8,  
    'verbose': -1
}

model = lgb.train(
    params,
    train_dataset,
    num_boost_round=300,
    valid_sets=[test_dataset],
    callbacks=[lgb.early_stopping(stopping_rounds=15, verbose=False)]
)

future_dates = pd.date_range(start=df['ds'].max() + pd.Timedelta(days=1), periods=90, freq='D')
last_sale = df['days_since_last_sale'].iloc[-1]

future_rows = []
for i, dt in enumerate(future_dates):
    row = {
        'month': dt.month,
        'day_of_week': dt.dayofweek,
        'day_of_month': dt.day,
        'quarter': dt.quarter,
        'is_weekend': 1 if dt.dayofweek in [5, 6] else 0,
        'sin_month': np.sin(2 * np.pi * dt.month / 12),
        'cos_month': np.cos(2 * np.pi * dt.month / 12),

    }
    future_rows.append(row)

X_future = pd.DataFrame(future_rows)
future_preds = model.predict(X_future)

results = pd.DataFrame({
    'date': future_dates.strftime('%Y-%m-%d'),
    'current_price': original_price,
    'predicted_price': np.round(future_preds, 2)
})

results['predicted_price'] = np.where(results['predicted_price'] > original_price - 0.5, original_price, results['predicted_price'])
results['predicted_price'] = np.where(((original_price - results['predicted_price']) / original_price) * 100 < 5, original_price, results['predicted_price'])

discount = ((original_price - results['predicted_price']) / original_price) * 100

results['estimated_discount'] = np.round(discount, 0).astype(int)

print(results.to_string(index=False))