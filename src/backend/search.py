import json
import os

ACRONYMS = {
    "cs": "counter-strike",
    "csgo": "counter-strike: global offensive",
    "cs2": "counter-strike 2",
    "gta": "grand theft auto",
    "gta v": "grand theft auto v",
    "gta 5": "grand theft auto v",
    "wow": "world of warcraft",
    "pubg": "playerunknown's battlegrounds",
    "cod": "call of duty",
    "rdr2": "red dead redemption 2",
    "eft": "escape from tarkov",
    "r6": "rainbow six",
    "r6s": "rainbow six siege",
    "tw3": "the witcher 3",
    "bg3": "baldur's gate 3",
    "nfs": "need for speed",
    "tf2": "team fortress 2",
    "aoe": "age of empires",
    "eso": "elder scrolls online",
    "ffxiv": "final fantasy xiv",
    "ff14": "final fantasy xiv",
    "ow": "overwatch",
    "ow2": "overwatch 2",
    "dbd": "dead by daylight",
    "rl": "rocket league",
    "tes": "the elder scrolls",
    "skyrim": "the elder scrolls v: skyrim",
    "poe": "path of exile",
    "hoi": "hearts of iron",
    "wt": "war thunder",
    "wot": "world of tanks",
    "fnaf": "five nights at freddy's"
}

game_index = []
is_loaded = False

def load_data():
    global game_index, is_loaded
    if is_loaded:
        return
    is_loaded = True

    path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'search_index.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            game_index.clear()
            game_index.extend(json.load(f))
    else:
        game_index.clear()

    price_map = {}
    discount_map = {}
    currency_map = {}
    prices_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'games_informations')
    if os.path.isdir(prices_dir):
        for fname in os.listdir(prices_dir):
            if not fname.startswith('games_chunk_') or not fname.endswith('.jsonl'):
                continue
            fpath = os.path.join(prices_dir, fname)
            try:
                with open(fpath, 'r', encoding='utf-8') as pf:
                    for line in pf:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            obj = json.loads(line)
                        except json.JSONDecodeError:
                            continue

                        try:
                            game_id_str, info = next(iter(obj.items()))
                        except Exception:
                            continue

                        if not isinstance(info, dict):
                            continue

                        po = info.get('price_overview')
                        if not po or not isinstance(po, dict):
                            continue

                        final = po.get('final')
                        if final is None:
                            continue

                        try:
                            fval = float(final)
                            price_pln = fval / 100.0
                            price_map[str(game_id_str)] = round(price_pln, 2)
                            discount_map[str(game_id_str)] = int(po.get('discount_percent') or 0)
                            currency_map[str(game_id_str)] = po.get('currency', 'PLN')
                        except Exception:
                            continue
            except Exception:

                continue

    for g in game_index:
        gid = str(g.get('id') or g.get('appid') or '')
        if gid in price_map:
            g['price'] = price_map[gid]
            g['discount'] = discount_map.get(gid, 0)
            g['currency'] = currency_map.get(gid, 'PLN')
        else:
            g.setdefault('price', 'Free')
            g.setdefault('discount', 0)
            g.setdefault('currency', 'PLN')

def search_games(query: str, limit=50, offset=0):
    if not is_loaded:
        load_data()
    
    if not query:
        return game_index[offset : offset + limit]

    q = query.lower()
    expanded_q = ACRONYMS.get(q, q)
    
    results = []
    count = 0
    for g in game_index:
        title_lower = g["title"].lower()
        if q in title_lower or expanded_q in title_lower:
            if count >= offset:
                results.append(g)
            count += 1
            if len(results) >= limit:
                break
    return results

def get_game_details(game_id: int):
    target_id = str(game_id)
    prices_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'games_informations')
    
    if not os.path.isdir(prices_dir):
        return {}
    
    for fname in os.listdir(prices_dir):
        if not fname.startswith('games_chunk_') or not fname.endswith('.jsonl'):
            continue
        
        fpath = os.path.join(prices_dir, fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    obj = json.loads(line)
                    if target_id in obj:
                        return obj[target_id]
        except Exception:
            continue
            
    return {}
def get_price_history(game_id: int):
    history = []
    prices_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'games_prices')
    
    if not os.path.isdir(prices_dir):
        return {"dates": [], "prices": []}
    
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
                                        history.append({"date": date, "price": price})
                    except json.JSONDecodeError:
                        continue
        except Exception:
            continue
    
    history.sort(key=lambda x: x["date"])
    dates = [h["date"] for h in history]
    prices = [h["price"] for h in history]
    
    return {"dates": dates, "prices": prices}
