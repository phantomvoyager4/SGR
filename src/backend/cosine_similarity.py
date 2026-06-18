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

def cs_recommender(movielist: list, limit: int = 15, offset: int = 0):
    _load_data_if_needed()
    
    valid_vectors = []
    valid_names = []
    
    for item in movielist:
        for movie, rating in item.items():
            idx = _name_to_index.get(movie)
            if idx is not None:
                weight = float(rating) / 10.0
                scaled_vector = _all_games_matrix_normalized[idx] * weight
                valid_vectors.append(scaled_vector)
                valid_names.append(movie)

    if not valid_vectors:
        return []

    meaner = np.mean(valid_vectors, axis=0, dtype=np.float32) 
    
    meaner_norm = np.linalg.norm(meaner)
    if meaner_norm == 0:
        return []
        
    meaner_normalized = (meaner / meaner_norm).astype(np.float32)
    
    similarities = np.dot(_all_games_matrix_normalized, meaner_normalized)

    for movie in valid_names:
        idx = _name_to_index.get(movie)
        if idx is not None:
            similarities[idx] = -1.0
            
    total_needed = offset + limit
    if total_needed > len(similarities):
        total_needed = len(similarities)
        
    if total_needed == 0 or offset >= len(similarities):
        return []

    top_indices = np.argpartition(similarities, -total_needed)[-total_needed:]
    top_indices_sorted = top_indices[np.argsort(-similarities[top_indices])]
    
    page_indices = top_indices_sorted[offset:total_needed]

    return [{_names_cached[idx]: round(float(similarities[idx]), 2)} for idx in page_indices]