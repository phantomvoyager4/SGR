"""Build the date from which each game was available on Steam.

Saves data/external/release_dates.parquet, indexed by appid, with columns:
- release_date:   release date from the Steam store data (NaT if unknown or unreleased)
- first_review:   date of the first review in recommendations.csv (NaT if no reviews)
- available_from: the earlier of the two, so early access games count from their first review
"""

import glob
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
GAMES_PATTERN = str(ROOT / "data/games_informations/games_chunk_*.jsonl")
REVIEWS_PATH = ROOT / "data/external/recommendations.csv"
OUTPUT_PATH = ROOT / "data/external/release_dates.parquet"


def load_release_dates(pattern=GAMES_PATTERN):
    """Read the release date of every game from the Steam store chunk files.

    pattern: glob pattern of the .jsonl chunk files, each line is {"<appid>": {...game info...}}

    Returns a Series indexed by appid. Text like "Coming soon", "To be announced"
    or "Q3 2026" cannot be parsed and becomes NaT (game not released yet).
    """
    rows = []
    for path in sorted(glob.glob(pattern)):
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    appid, info = next(iter(json.loads(line).items()))
                except (json.JSONDecodeError, StopIteration):
                    continue
                if isinstance(info, dict):
                    raw = (info.get("release_date") or {}).get("date", "")
                    rows.append((int(appid), raw))
    df = pd.DataFrame(rows, columns=["appid", "raw"]).drop_duplicates("appid", keep="last")
    df["release_date"] = pd.to_datetime(df["raw"], format="mixed", errors="coerce")
    return df.set_index("appid")["release_date"]


def load_first_reviews(path=REVIEWS_PATH):
    """Find the date of the first review of every game in the full reviews dataset.

    path: path to recommendations.csv (all reviews, before any filtering)

    Returns a Series indexed by appid.
    """
    reviews = pd.read_csv(path, usecols=["app_id", "date"], dtype={"app_id": "int32"}, parse_dates=["date"])
    first_review = reviews.groupby("app_id")["date"].min()
    first_review.index.name = "appid"
    return first_review


if __name__ == "__main__":
    release = load_release_dates()
    first_review = load_first_reviews()

    dates = pd.concat([release.rename("release_date"), first_review.rename("first_review")], axis=1)
    dates.index.name = "appid"
    # min() skips NaT, so a game with only one known date still gets that date
    dates["available_from"] = dates[["release_date", "first_review"]].min(axis=1)

    dates.to_parquet(OUTPUT_PATH)
    print(f"saved {len(dates):,} games to {OUTPUT_PATH}")
