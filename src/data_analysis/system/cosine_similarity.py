import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np




def cs_recommender(movielist:list):\

    def load_data(path='data/parquet/games_fully_vectorized.parquet'):
        df = pd.read_parquet(path)
        return df

    def vectorizer(movies_names:list, df):
        movie_dfs = {}
        for movie in movies_names:
            movie_dfs[movie] = df[df['name'] == movie]
        return movie_dfs


    df = load_data()
    vectors = vectorizer(movielist, df)
    for key, value in vectors.items():
        cleaned_df = value.drop(['index', 'name'], axis=1, errors='ignore')
        vectors[key] = cleaned_df.astype(float).to_numpy()
    valid_vectors = [n for n in vectors.values() if n.shape[0] > 0]

    if valid_vectors:
        meaner = np.mean(valid_vectors, axis=0)
        # print(f"Pomyślnie zsumowano {len(valid_vectors)} wektory po {meaner.shape[1]} cech.")
        
        # print(f"\nWeryfikacja algorytmu - szukam najbardziej podobnych gier do nowej średniej dla gier:\n{'\n'.join(movielist)}\n")
        all_games_matrix = df.drop(['index', 'name'], axis=1, errors='ignore').astype(float).to_numpy()
        similarities = cosine_similarity(meaner, all_games_matrix)

        parq_results = df.copy()
        parq_results['similarity'] = similarities[0]
        
        parq_results = parq_results[~parq_results['name'].isin(vectors.keys())]
        
        top_recommendations = parq_results[['name', 'similarity']].sort_values(by='similarity', ascending=False).head(15)
        server_return = [{row.name: round(row.similarity, 2)} for row in top_recommendations.itertuples(index=False)]
        return server_return
    
lmao = cs_recommender(['Counter-Strike', 'Counter-Strike: Condition Zero', 'Half-Life', 'Half-Life: Blue Shift'])
print(lmao)