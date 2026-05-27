# Steam Game Recommender (SGR)

### Tech stack:
1. Python backend (**FastAPI**),
2. Python data exploration (**scikit-learn - cosine similarity, pandas, numpy**),
3. React.js frontend (**Node.js, craco**),
4. **Docker** Containerization.

### How to run
1. go to this [google drive](https://drive.google.com/drive/folders/1hSaK7Kfyjcik1qe9EvCY70DOW7z_iiMU?usp=sharing) and download both index_table and parquet files,
2. Create a new folder called `parquet` in data folder and drop both previously downloaded files there,
3. Install **[Docker](https://www.docker.com/get-started/)** if you do not have it already,
4. Open terminal in project root and run command: 
```bash
docker compose up --build
```
3. If not opened, go to "localhost:3000/" on your internet browser,
4. Try out our recommendation system.

[Protoype website desing link in figma](https://www.figma.com/design/X0vyohfhJrMyU7qfeGo6Ll/Untitled?node-id=0-1&p=f&t=1YmrUn7rBX9DdiE7-0)