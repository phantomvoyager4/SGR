from fastapi import FastAPI, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from cosine_similarity import cs_recommender
from search import search_games, game_index, load_data, get_game_details, get_price_history

try:
    from discount_prediction import get_price_predictions
except ImportError:
    def get_price_predictions(game_id: str, days_ahead: int = 90):
        return {}

from pydantic import BaseModel
from typing import List, Dict

class RecommenderPayload(BaseModel):
    movie_list: List[Dict[str, float]]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def root():
    return('SGR')

@app.get('/search')
def search(q: str = "", limit: int = 50):
    return search_games(q, limit)

@app.get('/games')
def get_games(ids: str):
    load_data()
    id_set = set(ids.split(','))
    results = [g for g in game_index if str(g["id"]) in id_set]
    return results

@app.get('/health')
def health():
    return {"status": "ok"}

@app.get('/games_by_name')
def get_games_by_name(names: str):
    load_data()
    name_list = names.split('||')
    name_set = set(n.lower() for n in name_list)
    results = [g for g in game_index if g["title"].lower() in name_set]
    return results

@app.post('/recommender')
def recommend(payload: RecommenderPayload):
    response = cs_recommender(movielist=payload.movie_list)
    return response

@app.get('/game/{game_id}')
def get_game(game_id: int):
    load_data()
    return get_game_details(game_id)

@app.get('/game/{game_id}/price-history')
def get_game_price_history(game_id: int):
    return get_price_history(game_id)

@app.get('/game/{game_id}/price-predictions')
def get_game_predictions(game_id: str, days: int = 90):
    return get_price_predictions(game_id, days_ahead=days)

# kill -9 $(lsof -t -i:8000)
# uvicorn main:app --reload --port 8000