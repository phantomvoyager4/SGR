import json
import glob
import os

def build_index():
    index = []
    path = os.path.join('data', 'games_informations', '*.jsonl')
    out_path = os.path.join('data', 'search_index.json')
    files = glob.glob(path)
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line: continue
                try:
                    data = json.loads(line)
                    for game_id, game_data in data.items():
                        index.append({
                            "id": str(game_id),
                            "title": game_data.get("name", "Unknown"),
                            "cover": game_data.get("header_image", ""),
                            "genre": [g["description"] for g in game_data.get("genres", [])] if game_data.get("genres") else [],
                            "hours": 0,
                        })
                except Exception as e:
                    pass
    with open(out_path, 'w', encoding='utf-8') as out_f:
        json.dump(index, out_f)
    print("Done generating search_index.json with", len(index), "games.")

if __name__ == "__main__":
    build_index()
