import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os

_df_cached = None
_all_games_matrix_cached = None

def _load_data_if_needed():
    global _df_cached, _all_games_matrix_cached
    if _df_cached is None:
        path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'parquet', 'games_fully_vectorized.parquet')
        _df_cached = pd.read_parquet(path)
        _all_games_matrix_cached = _df_cached.drop(['index', 'name'], axis=1, errors='ignore').astype(float).to_numpy()

def cs_recommender(movielist:list):
    """
    This function is a recommender, based on cosine similarity. As an input, it takes list of game names, 
    which are then converted into vectors. After np.mean of this vectors, we find 10 games with most similar 
    vectors and return them as list of dictionaries: "game name": "similarity"
    """
    _load_data_if_needed()
    df = _df_cached
    all_games_matrix = _all_games_matrix_cached

    movie_dfs = {}
    for movie in movielist:
        movie_dfs[movie] = df[df['name'] == movie]

    vectors = movie_dfs
    for key, value in vectors.items():
        cleaned_df = value.drop(['index', 'name'], axis=1, errors='ignore')
        vectors[key] = cleaned_df.astype(float).to_numpy()
        
    valid_vectors = [n for n in vectors.values() if n.shape[0] > 0]

    if valid_vectors:
        meaner = np.mean(valid_vectors, axis=0)
        
        similarities = cosine_similarity(meaner, all_games_matrix)

        parq_results = df[['name']].copy()
        parq_results['similarity'] = similarities[0]
        
        parq_results = parq_results[~parq_results['name'].isin(vectors.keys())]
        
        top_recommendations = parq_results[['name', 'similarity']].sort_values(by='similarity', ascending=False).head(20)
        server_return = [{row.name: round(row.similarity, 2)} for row in top_recommendations.itertuples(index=False)]
        return server_return
    return []

# lmao = cs_recommender(['Counter-Strike', 'Counter-Strike: Condition Zero', 'Half-Life', 'Half-Life: Blue Shift'])
# print(lmao)