import pandas as pd
import numpy as np
import os

_matrix = None
_appids = None
_names = None
_appid_to_index = None

def _load_data_if_needed():
    global _matrix, _appids, _names, _appid_to_index
    if _matrix is not None:
        return

    path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'parquet', 'games_fully_vectorized.parquet')

    df = pd.read_parquet(path)

    _appids = df['appid'].to_numpy()
    _names = df['name'].to_numpy()
    _appid_to_index = {int(a): i for i, a in enumerate(_appids)}

    raw = df.drop(columns=['appid', 'name'], errors='ignore').astype(np.float32).to_numpy()
    del df

    norms = np.linalg.norm(raw, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    _matrix = raw / norms
    del raw

def recommend(games: dict[int, float], limit: int = 15, offset: int = 0):
    _load_data_if_needed()

    rows, weights = [], []
    for appid, rating in games.items():
        idx = _appid_to_index.get(int(appid))
        if idx is not None:
            rows.append(idx)
            weights.append(float(rating) / 10.0)

    if not rows or sum(weights) <= 0:
        return []

    profile = np.average(_matrix[rows], axis=0, weights=weights).astype(np.float32)
    profile_norm = np.linalg.norm(profile)
    if profile_norm == 0:
        return []
    profile /= profile_norm

    sims = _matrix @ profile
    # don't recommend the input games
    sims[rows] = -1.0

    k = min(offset + limit, len(sims))
    if k <= 0 or offset >= k:
        return []

    top = np.argpartition(sims, -k)[-k:]
    top = top[np.argsort(-sims[top])][offset:k]

    return [{"appid": int(_appids[i]), "name": _names[i], "similarity": round(float(sims[i]), 3)}
            for i in top]
