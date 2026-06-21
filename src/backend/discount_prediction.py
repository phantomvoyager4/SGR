import json
import os

try:
    import pandas as pd
    import numpy as np
    import lightgbm as lgb
    from sklearn.model_selection import train_test_split
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False

def get_price_predictions(game_id, days_ahead: int = 90):
    if not DEPS_AVAILABLE:
        return {}

    game_id = str(game_id)
    
    history = []
    prices_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'games_prices')
    
    if not os.path.isdir(prices_dir):
        print(f"Brak pliku {prices_dir}")
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
        print(f"Brak danych dla {game_id}")
        return {}
    
    try:
        df = pd.DataFrame(history)
        
        df['ds'] = pd.to_datetime(df['ds'], utc=True).dt.tz_convert(None).dt.normalize()
        df = df.drop_duplicates(subset=['ds'], keep='last').sort_values('ds')
        
        df.set_index('ds', inplace=True)
        df = df.resample('D').ffill()
        df.reset_index(inplace=True)
        df = df.dropna()
        
        # if len(df) < 10:
        #     return {}
        
        df['y'] = df['y'] / 100.0
        original_price = df['y'].max()
        
        sales_df = df[df['y'] < original_price - 0.5]
        typical_sale_price = sales_df['y'].median() if not sales_df.empty else original_price
        
        df['month'] = df['ds'].dt.month
        df['day_of_week'] = df['ds'].dt.dayofweek
        df['day_of_month'] = df['ds'].dt.day
        df['day_of_year'] = df['ds'].dt.dayofyear 
        df['quarter'] = df['ds'].dt.quarter
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        df['sin_month'] = np.sin(2 * np.pi * df['month'] / 12)
        df['cos_month'] = np.cos(2 * np.pi * df['month'] / 12)
        
        feature_cols = ['month', 'day_of_week', 'day_of_month', 'day_of_year', 'quarter', 'is_weekend', 'sin_month', 'cos_month']
        X = df[feature_cols]
        y = df['y']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        
        train_dataset = lgb.Dataset(X_train, label=y_train)
        test_dataset = lgb.Dataset(X_test, label=y_test, reference=train_dataset)
        
        params = {
            'objective': 'regression',
            'metric': 'mae',
            'boosting_type': 'gbdt',
            'learning_rate': 0.06,
            'num_leaves': 35,
            'min_data_in_leaf': 3,
            'feature_fraction': 1.0,
            'verbose': -1
        }
        
        model = lgb.train(
            params,
            train_dataset,
            num_boost_round=200,
            valid_sets=[test_dataset],
            callbacks=[lgb.early_stopping(stopping_rounds=20, verbose=False)]
        )
        
        start_date = pd.Timestamp.now().normalize()
        future_dates = pd.date_range(start=start_date, periods=days_ahead, freq='D')
        
        future_rows = []
        for dt in future_dates:
            row = {
                'month': dt.month,
                'day_of_week': dt.dayofweek,
                'day_of_month': dt.day,
                'day_of_year': dt.dayofyear, 
                'quarter': dt.quarter,
                'is_weekend': 1 if dt.dayofweek in [5, 6] else 0,
                'sin_month': np.sin(2 * np.pi * dt.month / 12),
                'cos_month': np.cos(2 * np.pi * dt.month / 12),
            }
            future_rows.append(row)
        
        X_future = pd.DataFrame(future_rows)
        future_preds = model.predict(X_future)
        
        threshold = original_price #* 0.99
        
        final_preds = []
        for p in future_preds:
            if p < threshold:
                final_preds.append(typical_sale_price)
            else:
                final_preds.append(original_price)
                
        final_preds = np.array(final_preds)
        discount = ((original_price - final_preds) / original_price) * 100
        
        return {
            "dates": future_dates.strftime('%Y-%m-%d').tolist(),
            "prices": np.round(final_preds, 2).tolist(),
            "discounts": np.round(discount, 0).astype(int).tolist(),
            "current_price": round(float(original_price), 2),
            "historical_dates": df['ds'].dt.strftime('%Y-%m-%d').tolist(),
            "historical_prices": df['y'].round(2).tolist(),
        }
    
    except Exception as e:
        print(f"Error predicting for game {game_id}: {str(e)}")
        return {}