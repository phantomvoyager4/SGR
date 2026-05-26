from fastapi import FastAPI, Query
from cosine_similarity import cs_recommender

app = FastAPI()

@app.get('/')
def root():
    return('xpppp')

@app.get('/recommender')
def recommend(movie_list: list = Query(...)):
    response = cs_recommender(movielist=movie_list)
    return response



# kill -9 $(lsof -t -i:8000)