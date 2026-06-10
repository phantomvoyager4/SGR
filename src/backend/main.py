from fastapi import FastAPI, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from cosine_similarity import cs_recommender
from search import search_games, game_index, load_data
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

# kill -9 $(lsof -t -i:8000)
# uvicorn main:app --reload --port 8000