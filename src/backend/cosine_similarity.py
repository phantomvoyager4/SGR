import pandas as pd
import numpy as np
import os

_all_games_matrix_normalized = None
_name_to_index = None
_names_cached = None

def _load_data_if_needed():
    global _all_games_matrix_normalized, _name_to_index, _names_cached
    if _all_games_matrix_normalized is not None:
        return

    path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'parquet', 'games_fully_vectorized.parquet')
    
    df = pd.read_parquet(path)
    
    _names_cached = df['name'].to_numpy()
    _name_to_index = {name: idx for idx, name in enumerate(_names_cached)}

    raw_matrix = df.drop(['index', 'name'], axis=1, errors='ignore').astype(np.float32).to_numpy()
    del df
    
    norms = np.linalg.norm(raw_matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    _all_games_matrix_normalized = raw_matrix / norms
    del raw_matrix

def cs_recommender(movielist: list):
    _load_data_if_needed()
    
    valid_vectors = []
    
    for movie in movielist:
        idx = _name_to_index.get(movie)
        if idx is not None:
            valid_vectors.append(_all_games_matrix_normalized[idx])

    if not valid_vectors:
        return []

    meaner = np.mean(valid_vectors, axis=0, dtype=np.float32) 
    
    meaner_norm = np.linalg.norm(meaner)
    if meaner_norm == 0:
        return []
        
    meaner_normalized = (meaner / meaner_norm).astype(np.float32)
    
    similarities = np.dot(_all_games_matrix_normalized, meaner_normalized)

    for movie in movielist:
        idx = _name_to_index.get(movie)
        if idx is not None:
            similarities[idx] = -1.0
            
    k = min(20, len(similarities))
    top_indices = np.argpartition(similarities, -k)[-k:]
    top_indices_sorted = top_indices[np.argsort(-similarities[top_indices])]

    return [{_names_cached[idx]: round(float(similarities[idx]), 2)} for idx in top_indices_sorted]