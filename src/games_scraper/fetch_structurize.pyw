import os
import json
import requests
import time
import glob
from dotenv import load_dotenv

def get_script_dir():
    return os.path.dirname(os.path.abspath(__file__))

def load_api_key():
    """
    Load Steam API keys from the .env file located in the .venv folder.
    """
    # Use path relative to the script location (.venv is parallel to src, so ../.venv)
    env_path = os.path.join(get_script_dir(), "..", ".venv", ".env")
    
    load_dotenv(dotenv_path=env_path)
    access_token = os.getenv('access_token')
    web_api_key = os.getenv('web_api_key')
    return access_token, web_api_key

def get_games_raw_data(app_id):
    """
    Fetch detailed store information for a specific game by its App ID.
    Saves the raw JSON response to a local file and returns the parsed game data.
    """
    url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
    response = requests.get(url)
    
    data = None
    game_name = None
    
    if response.status_code == 200:
        try:
            data = response.json()
            str_app_id = str(app_id)
            game_name = data[str_app_id]["data"]["name"]
        except KeyError:
            print(f"Skipping {app_id}: No valid store data or name found.")
    else:
        print(f"Failed to fetch {app_id}. Status code: {response.status_code}")
        
    return data, game_name, response.status_code

def structurize_game_output(raw: dict, gamename):
    first_key = list(raw.keys())[0]
    if isinstance(raw.get(first_key), dict) and "data" in raw[first_key]:
        raw_data = raw[first_key]["data"]
    else:
        raw_data = raw
        
    to_pop = ["type", "steam_appid", "required_age", "detailed_description", "short_description",
              "capsule_image", "capsule_imagev5", "website", "pc_requirements","mac_requirements",
              "packages", "package_groups", "linux_requirements", "platforms", "metacritic", 
              "screenshots", "background", "background_raw", "content_descriptors", "ratings",
              "movies", "legal_notice"]        
    for att in to_pop:
        raw_data.pop(att, None)

    to_pop_price_overview = ["initial_formatted", "final_formatted"]
    if "price_overview" in raw_data:
        for att in to_pop_price_overview:
            if att in raw_data["price_overview"]:
                raw_data["price_overview"].pop(att)
    
    if not raw_data.get("achievements"):
        raw_data["achievements"] = None
    
    raw_data["game_link"] = f"https://store.steampowered.com/app/{first_key}/{gamename}/"

    structurized = {}
    structurized[first_key] = raw_data
        
    return structurized

def main():
    access_token, web_api_key = load_api_key()
    
    base_dir = os.path.join(get_script_dir(), "..")
    data_dir = os.path.join(base_dir, "data")
    output_dir = os.path.join(data_dir, "games_informations")
    os.makedirs(output_dir, exist_ok=True)
    
    all_ids = []
    games_id_path = os.path.join(data_dir, 'games_id_all.json')
    
    if not os.path.exists(games_id_path):
        print(f"File not found: {games_id_path}. Please generate the IDs first.")
        return

    with open(games_id_path, 'r', encoding='utf-8') as f:
        games_id = json.load(f)
        
    if "response" in games_id and "apps" in games_id["response"]:
        for app in games_id["response"]["apps"]:
            all_ids.append(app["appid"])

    print(f"Total IDs loaded: {len(all_ids)}") #162941

    # 1. Read existing attempted IDs (both successful and failed are stored here)
    attempted_file = os.path.join(output_dir, "attempted_ids.txt")
    existing_app_ids = set()

    if os.path.exists(attempted_file):
        with open(attempted_file, "r", encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Handle lines with status codes (e.g., "12345 200")
                parts = line.split()
                if parts and parts[0].isdigit():
                    existing_app_ids.add(int(parts[0]))

    print(f"Found {len(existing_app_ids)} already attempted games.")

    # 2. Logic for chunked files
    max_lines = 10000
    chunk_index = 1

    # Find the current highest chunk index
    existing_chunks = glob.glob(os.path.join(output_dir, "games_chunk_*.jsonl"))
    if existing_chunks:
        indexes = []
        for chunk in existing_chunks:
            try:
                # Extract number from 'games_chunk_X.jsonl'
                idx = int(os.path.basename(chunk).split('_')[2].split('.')[0])
                indexes.append(idx)
            except ValueError:
                pass
        if indexes:
            chunk_index = max(indexes)

    current_chunk_file = os.path.join(output_dir, f"games_chunk_{chunk_index}.jsonl")

    # 3. Fetch missing ones
    for n in all_ids:
        if n in existing_app_ids:
            # Already downloaded or attempted, skip to next without hitting the API
            continue
            
        rawww, gamename, status_code = get_games_raw_data(n)
        time.sleep(1.5)  # Protection limit
        
        if gamename is not None and rawww is not None:
            # Structurize and write one line to the JSONL file
            structurized_data = structurize_game_output(rawww, gamename)
            
            # Check current chunk file lines limit
            if os.path.exists(current_chunk_file):
                with open(current_chunk_file, 'r', encoding="utf-8") as temp_f:
                    line_count = sum(1 for line in temp_f)
                if line_count >= max_lines:
                    chunk_index += 1
                    current_chunk_file = os.path.join(output_dir, f"games_chunk_{chunk_index}.jsonl")
                
            with open(current_chunk_file, "a", encoding="utf-8") as chunk_f:
                chunk_f.write(json.dumps(structurized_data) + "\n")
                
            print(f"Saved JSON for {gamename} (AppID: {n}) in chunk {chunk_index}")
            
            # Append logic added to only write to txt if fetch was successfully done
            existing_app_ids.add(n)
            with open(attempted_file, "a", encoding='utf-8') as f:
                f.write(f"{n} {status_code}\n")
        else:
            print(f"Recorded failed/invalid request for AppID: {n}")
            # Also record failed attempts so we don't try them again
            existing_app_ids.add(n)
            with open(attempted_file, "a", encoding='utf-8') as f:
                f.write(f"{n} {status_code}\n")

if __name__ == "__main__":
    main()