import os
from dotenv import load_dotenv
import requests

def load_api_key():
    """
    Load Steam API keys from the .env file located in the .venv folder.
    
    Returns:
        tuple: A tuple containing (api_key).
    """
    # Notebook is in the 'src/' folder, so go up one level to reach '.venv/.env'
    env_path = 'SGR\src\config.env'
    
    load_dotenv(dotenv_path=env_path)
    api_key = os.getenv('itd_api_key')
    return api_key

api_key = load_api_key()

game_id = 4000

URL = 'https://api.isthereanydeal.com/games/history/v2'

params = {
    'key': api_key,
    'id': game_id,
    'shops': 61,
    'country': 'PL'
}

response = requests.get(URL, params=params)

if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print(f"Error: {response.status_code}")