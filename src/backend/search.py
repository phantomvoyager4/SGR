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
    if is_loaded: return
    is_loaded = True

    path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'search_index.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            game_index.clear()
            game_index.extend(json.load(f))
    else:
        game_index.clear()

def search_games(query: str, limit=50):
    if not is_loaded:
        load_data()
    
    if not query:
        return game_index[:limit]

    q = query.lower()
    expanded_q = ACRONYMS.get(q, q)
    
    results = []
    for g in game_index:
        title_lower = g["title"].lower()
        if q in title_lower or expanded_q in title_lower:
            results.append(g)
            if len(results) >= limit:
                break
    return results
