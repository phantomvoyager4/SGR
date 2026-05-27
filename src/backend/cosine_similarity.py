import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os

_df_cached = None
_all_games_matrix_cached = None
_all_games_matrix_normalized = None
_name_to_index = None
_names_cached = None

def _load_data_if_needed():
    global _all_games_matrix_cached, _all_games_matrix_normalized, _name_to_index, _names_cached
    if _all_games_matrix_normalized is None:
        path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'parquet', 'games_fully_vectorized.parquet')
        df = pd.read_parquet(path)
        
        # Build a fast mapping for row lookups
        _names_cached = df['name'].to_numpy()
        _name_to_index = {name: idx for idx, name in enumerate(_names_cached)}

        _all_games_matrix_cached = df.drop(['index', 'name'], axis=1, errors='ignore').astype(np.float32).to_numpy()
        
        # Free memory forcibly to prevent Docker OOM
        del df
        import gc
        gc.collect()
        import ctypes
        import ctypes.util
        try:
            libc = ctypes.CDLL(ctypes.util.find_library('c'))
            libc.malloc_trim(0)
        except Exception:
            pass
        
        # Pre-normalize for instant cosine distance scoring
        norms = np.linalg.norm(_all_games_matrix_cached, axis=1, keepdims=True)
        # Avoid division by zero
        norms[norms == 0] = 1.0
        _all_games_matrix_normalized = _all_games_matrix_cached / norms

def cs_recommender(movielist:list):
    """
    This function is a recommender, based on cosine similarity. As an input, it takes list of game names, 
    which are then converted into vectors. After np.mean of this vectors, we find 10 games with most similar 
    vectors and return them as list of dictionaries: "game name": "similarity"
    """
    _load_data_if_needed()
    
    valid_vectors = []
    
    for movie in movielist:
        idx = _name_to_index.get(movie)
        if idx is not None:
            valid_vectors.append(_all_games_matrix_cached[idx])

    if valid_vectors:
        meaner = np.mean(valid_vectors, axis=0) # 1D array
        
        # Calculate cosine similarity using the pre-normalized matrix
        meaner_norm = np.linalg.norm(meaner)
        if meaner_norm == 0:
            return []
            
        meaner_normalized = meaner / meaner_norm
        
        # dot product with (N, feats) @ (feats,) -> (N,)
        similarities = np.dot(_all_games_matrix_normalized, meaner_normalized)

        # Exclude original movies by setting their similarity to -1
        for movie in movielist:
            idx = _name_to_index.get(movie)
            if idx is not None:
                similarities[idx] = -1.0
                
        # Use argpartition to get top 20 indices
        k = min(20, len(similarities))
        top_indices = np.argpartition(similarities, -k)[-k:]

        # Sort the top 20 indices by actual similarity values
        top_indices_sorted = top_indices[np.argsort(-similarities[top_indices])]

        # Build the return dictionary
        server_return = [{_names_cached[idx]: round(float(similarities[idx]), 2)} for idx in top_indices_sorted]
        return server_return
    return []

# lmao = cs_recommender(['Counter-Strike', 'Counter-Strike: Condition Zero', 'Half-Life', 'Half-Life: Blue Shift'])
# print(lmao)