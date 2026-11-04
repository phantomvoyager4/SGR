# Steam Game Recommender (SGR)

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-00a393?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19-61dafb?logo=react&logoColor=black)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Machine_Learning-F7931E?logo=scikit-learn&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

**Steam Game Recommender (SGR)** is a full-stack, machine-learning-powered web application that provides highly accurate, personalized game recommendations out of a dataset spanning over **162,000+ Steam games**.

By leveraging **Cosine Similarity** on fully vectorized game features (genres, tags, descriptions), SGR can instantly find titles similar to a user's selected favorites.

## Key Features

- **Blazing Fast ML Inference**: The recommendation engine runs pure linear algebra (`np.dot` with pre-normalized vectors) on `float32` matrices. Compute times for recommendations plummeted from ~16 seconds down to **~130ms**.
- **Smart Game Search**: Includes an intuitive search bar with automated acronym mapping (e.g., searching `cs2` routes to `Counter-Strike 2`, `gta v` routes to `Grand Theft Auto V`).
- **Performance & Memory Optimized**: Designed to run efficiently in Docker containers using Python Garbage Collection overrides to process huge Parquet matrices without triggering OS-level OOM (Out-of-Memory) killers.
- **Modern UI/UX**: Built with React and Tailwind CSS, featuring snappy animations, responsive layouts, and interactive game cards.
- **End-to-End Pipeline**: Includes complete automated web scraping, data structurization, and ML vectorization pipelines under the hood.

## Tech Stack

### Data Science & Machine Learning

- **Pandas & NumPy**: For heavy data manipulation and multidimensional matrix math.
- **Scikit-Learn**: For feature extraction and vector space modeling.
- **PyArrow (Parquet)**: Highly compressed, columnar data storage for rapid dataset hydration.

### Backend (API)

- **FastAPI & Uvicorn**: Delivering a high-throughput, async REST API.
- **Python 3.12**: Handling file systems, advanced hardware-level garbage collection, and request routing.

### Frontend

- **React (via CRA/Craco) & React Router**: Dynamic client-side routing and state management.
- **Tailwind CSS & Lucide Icons**: Modern dashboard styling and responsive components.

### DevOps

- **Docker & Docker Compose**: Fully containerized multi-tier architecture with live-reloading tied via mounted volumes.

## Project Structure

```text
SGR/
├── data/                    # Local datasets (JSONL, Parquet, Search Index)
├── docs/                    # Walkthroughs & generated plots
├── src/
│   ├── backend/             # FastAPI App, ML inference & Dockerfile (production code)
│   ├── frontend/            # React Codebase, Tailwind configs & Dockerfile
│   ├── data_analysis/       # Everything exploratory/offline, kept out of backend/
│   │   ├── vectorization/   # Feature engineering pipeline (run.py + vectorization_script.py)
│   │   ├── visualization/   # UMAP/DBSCAN cluster notebook
│   │   ├── validation/      # One-off data QA scripts (e.g. price_file_validate.py)
│   │   ├── system_evaluation/ # Offline evaluation of the recommender (hit rate vs baselines)
│   │   └── experiments/     # Superseded/prototype scripts kept for reference
│   └── games_scraper/       # Fetch & Structurize Scripts for Steam Data (incl. price_fetcher.ipynb)
├── run_dev.py               # Convenience script: launches backend + frontend dev servers locally
└── docker-compose.yml       # Orchestrates the containers
```

## Getting Started

Follow these steps to run the project locally on your machine.

### Prerequisites

1. Install **[Docker Engine](https://www.docker.com/get-started/)** and ensure it's running.
2. Download the pre-computed ML dataset models.

### Installation

1. **Download the Vectorized Database**:
   - Navigate to our [Google Drive Data Repository](https://drive.google.com/drive/folders/1hSaK7Kfyjcik1qe9EvCY70DOW7z_iiMU?usp=sharing).
   - Download the `index_table.xlsx` and the `.parquet` files.
2. **Mount the Data**:
   - Inside the repository's `data/` directory, create a folder named `parquet`.
   - Place the downloaded files directly into `data/parquet/`.
3. **Build and Run via Docker**:
   Open a terminal in the project root and spin up the containers:
   ```bash
   docker compose up -d --build
   ```
4. **Access the App**:
   - **Frontend UI**: Go to [http://localhost:3000](http://localhost:3000)
   - **Backend API Docs**: Go to [http://localhost:8000/docs](http://localhost:8000/docs)

## How the Recommender Works

1. **Scraping**: `games_scraper/` routinely hits Steam APIs to retrieve massive chunks of raw `.jsonl` data.
2. **Vectorization**: We clean descriptions, tags, and genres, then vectorize them into a `float32` matrix, finally storing it as a highly compressed `.parquet` file.
3. **Inference**: When a user selects games in their browser, the frontend passes them to FastAPI. The backend looks up the games in an `O(1)` dictionary, pulls their multi-dimensional pre-normalized vectors, averages them (`np.mean`), and calculates distance against the entire **162,000x4,098** matrix dynamically using Numpy dot operations (`np.dot`). The closest similarities are sorted via `argpartition` and returned to the UI instantly.

### Visualizing the Recommendation Space

To sanity-check that the vectorized feature space actually groups similar games together, `src/data_analysis/visualization/vis.ipynb` projects the full **4,098-dimensional** game vectors down to 2D with TruncatedSVD + UMAP, then runs DBSCAN over that projection to surface thematic neighborhoods. Each dense blob below is a cluster of games the recommender considers close in cosine-similarity space; scattered gray points are unclustered "noise" games.

![UMAP projection of Steam games colored by DBSCAN cluster](docs/plots/umap_clusters.png)

*Static preview above — [open the interactive version](docs/plots/umap_clusters.html) (download and open locally) to pan, zoom, and hover individual game titles.*

## Evaluation

`src/data_analysis/system_evaluation/` measures how well SGR predicts the next game a real user liked, using the [Game Recommendations on Steam](https://www.kaggle.com/datasets/antonkozyriev/game-recommendations-on-steam?resource=download&select=recommendations.csv) dataset from Kaggle (`recommendations.csv`, ~41M user reviews).

**Method: chronological leave-one-out.** For each user, the most recent liked game is held out as the `target` and the earlier ones are the `history`. SGR gets the history as input, and it's a hit at K if the target is in its top K recommendations (HR@K). SGR is compared with two baselines: **Most popular** (the most liked games, a strong baseline on Steam data) and **Random**. Every method only recommends games that were already out on the day the user reviewed the target.

**Files**

| File                              | What it does                                                                                                                              | Output                                       |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| `prepare_evaluation_data.ipynb` | Keeps positive reviews of games that have a feature vector, from users with 4–10 liked games, and splits each user into history + target | `data/external/recommendations_ready.json` |
| `prepare_release_dates.py`      | Finds the date each game became available: the earlier of the Steam release date and its first review                                     | `data/external/release_dates.parquet`      |
| `evaluation_system.ipynb`       | Runs the evaluation on a sample of 2,000 users (one seed) and a popularity-boost experiment                                               | `evaluation_report.txt`                    |
| `run_seeds.py`                  | Runs the notebook for 6 seeds and combines the results, with 95% intervals                                                                | `reports/`                                 |

**Reproduce it**

1. Download `recommendations.csv` from the Kaggle link above into `data/external/`.
2. Make sure `data/parquet/games_fully_vectorized.parquet` (see [Installation](#installation)) and the scraped `data/games_informations/games_chunk_*.jsonl` files are in place.
3. Run `prepare_evaluation_data.ipynb`, then `python prepare_release_dates.py`.
4. Run `evaluation_system.ipynb` for one sample, or `python run_seeds.py` for all seeds (about 2.5 minutes per seed).

**Results** (pooled over 6 seeds, 12,000 users, from `reports/evaluation_report_seeds.txt`)

|       | SGR   | Most popular | Random (expected) |
| ----- | ----- | ------------ | ----------------- |
| HR@5  | 1.22% | 2.43%        | 0.014%            |
| HR@10 | 1.80% | 4.37%        | 0.027%            |
| HR@20 | 2.78% | 7.05%        | 0.055%            |

- SGR finds the user's next game about **50x as often as random**, so the feature vectors carry real signal.
- **Most popular beats plain SGR**, because users often go on to like a hit, while SGR recommends similar but often niche games.
- **Adding popularity fixes that.** Scoring games by `SGR + ALPHA × popularity` with ALPHA ≈ 1 reaches **8.7% HR@20**, above both SGR alone and the popularity baseline. This experiment lives only in the notebook; the app still uses plain SGR.

![HR@K by popularity boost ALPHA, mean of 6 seeds](src/data_analysis/system_evaluation/reports/hr_by_alpha_seeds.png)

## Design

The original prototype and user experience framework were designed on Figma.
[View Figma Design Specs](https://www.figma.com/design/X0vyohfhJrMyU7qfeGo6Ll/Untitled?node-id=0-1&p=f&t=1YmrUn7rBX9DdiE7-0)
