import json
import os

import numpy as np
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
MATRIX_PATH = os.path.join(DATA_DIR, 'parquet', 'games_fully_vectorized.parquet')
# Steam review count of every game, built by data/games_informations/extract_recommendations.py
REVIEW_COUNTS_PATH = os.path.join(DATA_DIR, 'games_informations', 'recommendations_count.json')

# score = cosine similarity + POPULARITY_WEIGHT * popularity. The weight was picked on separate tuning users
# and checked on unseen test users in src/data_analysis/system_evaluation/evaluation_system.ipynb (ALPHA for
# Steam review counts, reports/selected_alpha.json), where it raised HR@15 from 2.17% to 7.08%.
POPULARITY_WEIGHT = 0.8

_matrix = None
_appids = None
_names = None
_appid_to_index = None
_popularity = None

def _load_data_if_needed():
    global _matrix, _appids, _names, _appid_to_index, _popularity
    if _matrix is not None:
        return

    df = pd.read_parquet(MATRIX_PATH)

    _appids = df['appid'].to_numpy()
    _names = df['name'].to_numpy()
    _appid_to_index = {int(a): i for i, a in enumerate(_appids)}

    raw = df.drop(columns=['appid', 'name'], errors='ignore').astype(np.float32).to_numpy()
    del df

    norms = np.linalg.norm(raw, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    _matrix = raw / norms
    del raw

    _popularity = _load_popularity(_appids)

def _load_popularity(appids):
    """Popularity of every game in the matrix's row order, scaled to 0-1.

    log(1 + Steam review count), divided by the same value of the most reviewed game. The log stops a few huge
    hits from taking over. Steam leaves out the count for games with about 100 reviews or fewer, so they get 0.
    """
    with open(REVIEW_COUNTS_PATH, encoding='utf-8') as f:
        counts = {int(appid): count for appid, count in json.load(f).items()}

    log_counts = np.log1p(np.array([counts.get(int(a), 0) for a in appids], dtype=np.float64))
    return (log_counts / log_counts.max()).astype(np.float32)

def recommend(games: dict[int, float], limit: int = 15, offset: int = 0,
              popularity_weight: float = POPULARITY_WEIGHT):
    """Games most similar to the given ones, boosted by popularity.

    games:             app id -> rating 1-10, used as the weight of the game in the user's profile
    popularity_weight: how much popularity adds to the score; 0 ranks by cosine similarity alone

    Returns the games ranked offset..offset+limit, without the input games. "similarity" is the cosine
    similarity to the profile, without the popularity boost.
    """
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
    scores = sims + np.float32(popularity_weight) * _popularity
    # don't recommend the input games
    scores[rows] = -np.inf

    k = min(offset + limit, len(scores) - len(set(rows)))
    if k <= 0 or offset >= k:
        return []

    top = np.argpartition(scores, -k)[-k:]
    top = top[np.argsort(-scores[top])][offset:k]

    return [{"appid": int(_appids[i]), "name": _names[i], "similarity": round(float(sims[i]), 3)}
            for i in top]
