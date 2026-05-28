import json
import pandas as pd
from prophet import Prophet

chunk = 1
records = []

with open(f"data/games_prices/price_data_chunk_{chunk}.jsonl", 'r') as f:
    for line in f:
        try:
            data = json.loads(line)
            for game_id, prices_list in data.items():
                if isinstance(prices_list, list):
                    for price_dict in prices_list:
                        if isinstance(price_dict, dict):
                            for timestamp, price in price_dict.items():
                                records.append({'id': game_id, 'timestamp': timestamp, 'price': price})
        except json.JSONDecodeError:
            continue

df = pd.DataFrame(records)

target_game = "500"  

df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True).dt.tz_localize(None)
