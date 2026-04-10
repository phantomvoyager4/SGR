import json 
import requests

from dotenv import load_dotenv
import os

from datetime import datetime

def load_api_key():
    """
    Load Steam API keys from the .env file located in the .venv folder.
    
    Returns:
        tuple: A tuple containing (access_token, web_api_key).
    """
    # Tell load_dotenv exactly where the .env file is
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.venv', '.env')
    
    # Or simply Use a hardcoded relative path if you run it from the root directory:
    # env_path = ".venv/.env" 
    
    load_dotenv(dotenv_path=env_path)
    
    access_token = os.getenv('access_token')
    web_api_key = os.getenv('web_api_key')
    return access_token, web_api_key

access_token, web_api_key = load_api_key()

def get_apps_id():
    """
    Fetch the list of all Steam applications (games, software, etc.) and their IDs.
    
    Returns:
        dict: JSON response containing the list of apps if successful, None otherwise.
    """
    url = f"https://api.steampowered.com/IStoreService/GetAppList/v1/?access_token={access_token}"
    response = requests.get(url)
    if response.status_code == 200:
        games_data = response.json()
        return games_data
        # output_path = "data/games_info.json"
        # with open(output_path, "w") as f:
        #     json.dump(games_data, f)
    else: 
        print(f"error:{response.status_code}")

games_raw = get_apps_id()

def get_games_data(app_id):
    """
    Fetch detailed store information for a specific game by its App ID.
    Saves the raw JSON response to a local file and returns the parsed game data.
    
    Args:
        app_id (int or str): The Steam Application ID to fetch data for.
        
    Returns:
        dict: The game's store data details if successful, None otherwise.
    """
    url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        output_path = f"data/{app_id}.json"
        with open(output_path, "w") as f:
            json.dump(data, f)
        str_app_id = str(app_id)
        
        if data and data.get(str_app_id) and data[str_app_id].get('success'):
            game_info = data[str_app_id]['data']
            return game_info
        else:
            print(f"Error: Game {app_id} does not have standard store info available.")
    else:
        print(f"Failed to fetch {app_id}. Status code: {response.status_code}")
        
    return None


cs2id = games_raw["response"]['apps'][0]["appid"]

get_games_data(cs2id)