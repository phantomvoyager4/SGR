import json
import glob
import os

game_index = []
is_loaded = False

def load_data():
    global game_index, is_loaded
    if is_loaded: return
    is_loaded = True
    
    temp_index = []
    path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'games_informations', '*.jsonl')
    files = glob.glob(path)
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line: continue
                try:
                    data = json.loads(line)
                    for game_id, game_data in data.items():
                        # Save relevant info
                        temp_index.append({
                            "id": game_id,
                            "title": game_data.get("name", "Unknown"),
                            "cover": game_data.get("header_image", ""),
                            "genre": [g["description"] for g in game_data.get("genres", [])] if game_data.get("genres") else [],
                            "hours": 0 # Default placeholder
                        })
                except json.JSONDecodeError:
                    continue
    game_index.extend(temp_index)

def search_games(query: str, limit=50):
    if not is_loaded:
        load_data()
    
    if not query:
        return game_index[:limit]

    q = query.lower()
    results = []
    for g in game_index:
        if q in g["title"].lower():
            results.append(g)
            if len(results) >= limit:
                break
    return results
