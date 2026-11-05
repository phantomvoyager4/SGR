"""Steam review count of every game in games_chunk_*.jsonl, saved as recommendations_count.json.

Each line of a chunk is {"<appid>": {..., "recommendations": {"total": N}}}. Steam's appdetails API leaves out
"recommendations" for games with about 100 reviews or fewer, so those games get 0.
"""
import json
from pathlib import Path

GAMES_DIR = Path(__file__).resolve().parent  # works from any working directory
OUT_PATH = GAMES_DIR / "recommendations_count.json"

recommendations = {}  # appid -> Steam review count
for path in sorted(GAMES_DIR.glob("games_chunk_*.jsonl")):
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            (appid, game), = json.loads(line).items()  # each line is {"<appid>": {...}}
            recommendations[int(appid)] = game.get("recommendations", {}).get("total", 0)

OUT_PATH.write_text(json.dumps(recommendations))
print(f"{len(recommendations):,} games, {sum(v > 0 for v in recommendations.values()):,} with reviews")
print(f"saved to {OUT_PATH}")
