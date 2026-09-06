import json
import os
import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split

def get_price_predictions(game_id: str, days_ahead: int = 90):
    """
    Get discount predictions for a game by analyzing historical price data.
    
    Args:
        game_id: Steam game ID as string
        days_ahead: Number of days to predict (default 90)
    
    Returns:
        dict with keys: dates, prices, discounts, current_price, or empty dict if no data
    """
    history = []
    prices_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'games_prices')
    
    if not os.path.isdir(prices_dir):
        return {}
    
    for fname in sorted(os.listdir(prices_dir)):
        if not fname.startswith('price_data_chunk_') or not fname.endswith('.jsonl'):
            continue
        
        fpath = os.path.join(prices_dir, fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        if game_id in obj and isinstance(obj[game_id], list):
                            for entry in obj[game_id]:
                                if isinstance(entry, dict):
                                    for date, price in entry.items():
                                        history.append({"ds": date, "y": price})
                    except json.JSONDecodeError:
                        continue
        except Exception:
            continue
    
    if not history:
        return {}
    
    try:
        df = pd.DataFrame(history)
        df['ds'] = pd.to_datetime(df['ds'])
        df = df.drop_duplicates(subset=['ds']).sort_values('ds')
        
        df.set_index('ds', inplace=True)
        df = df.resample('D').ffill()
        df.reset_index(inplace=True)
        
        df = df.dropna()
        df = df.sort_values('ds')
        
        if len(df) < 10:
            return {}
        
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
        
        if len(X) < 5:
            return {}
        
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
        
        future_dates = pd.date_range(start=df['ds'].max() + pd.Timedelta(days=1), periods=days_ahead, freq='D')
        
        future_rows = []
        for dt in future_dates:
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
        
        future_preds = np.where(future_preds > original_price - 0.5, original_price, future_preds)
        future_preds = np.where(((original_price - future_preds) / original_price) * 100 < 5, original_price, future_preds)
        
        discount = ((original_price - future_preds) / original_price) * 100
        
        return {
            "dates": future_dates.strftime('%Y-%m-%d').tolist(),
            "prices": np.round(future_preds, 2).tolist(),
            "discounts": np.round(discount, 0).astype(int).tolist(),
            "current_price": round(float(original_price), 2),
            "historical_dates": df['ds'].dt.strftime('%Y-%m-%d').tolist(),
            "historical_prices": df['y'].round(2).tolist(),
        }
    
    except Exception as e:
        print(f"Error predicting for game {game_id}: {str(e)}")
        return {}
