import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np




#CS
# Steelborn = df[df['name'] == 'Ambush'] 
# Steelborn = Steelborn.drop(['index', 'name'], axis=1)

# HDQ = df[df['name'] == 'HuGe']
# HDQ = HDQ.drop(['index', 'name'], axis=1)
# cos = cosine_similarity(Steelborn, HDQ)
# print(cos[0][0])



# m1 = HDQ.astype(float).to_numpy()
# m2 = Steelborn.astype(float).to_numpy()
# srednia = (m1 + m2) / 2
# print(m1, m2, srednia)

def load_data(path='data/parquet_example/games_fully_vectorized.parquet'):
    df = pd.read_parquet(path)
    return df


def cosine_similarity_recommender(movies_names:list, df):
    movie_dfs = {}
    for movie in movies_names:
        movie_dfs[movie] = df[df['name'] == movie]
    return movie_dfs


parq = load_data()
dicto = cosine_similarity_recommender(['Counter-Strike', 'Counter-Strike: Condition Zero', 'Half-Life', 'Half-Life: Blue Shift'], parq)
for key, value in dicto.items():
    cleaned_df = value.drop(['index', 'name'], axis=1, errors='ignore')
    dicto[key] = cleaned_df.astype(float).to_numpy()



# Odfiltrowujemy puste wektory (np. gdy gry nie znaleziono w DataFrame)
valid_vectors = [n for n in dicto.values() if n.shape[0] > 0]

if valid_vectors:
    # np.mean musi otrzymać listę lub tablicę numpy, by poprawnie policzyć średnią wertykalnie
    meaner = np.mean(valid_vectors, axis=0)
    print(f"Pomyślnie zsumowano {len(valid_vectors)} wektorów po {meaner.shape[1]} cech.")
    
    print("\nWeryfikacja algorytmu - szukam najbardziej podobnych gier do nowej średniej...")
    
    # 1. Przygotowujemy całą bazę do ujednoliconej macierzy (odrzucamy tekstowe kolumny)
    all_games_matrix = parq.drop(['index', 'name'], axis=1, errors='ignore').astype(float).to_numpy()
    
    # 2. Obliczamy podobieństwo cosinusowe pomiędzy średnim wektorem (meaner) a CAŁĄ BAZĄ
    similarities = cosine_similarity(meaner, all_games_matrix)
    
    # 3. Przypisujemy wyniki do ramki danych
    parq_results = parq.copy()
    parq_results['similarity'] = similarities[0]
    
    # Odfiltrowujemy gry, które posłużyły za bazę (wartości z dicto.keys()), żeby system nie polecał ich samych
    parq_results = parq_results[~parq_results['name'].isin(dicto.keys())]
    
    # 4. Sortujemy malejąco i wypisujemy Top 15 najbliższych trafień
    top_recommendations = parq_results[['name', 'similarity']].sort_values(by='similarity', ascending=False).head(15)
    
    print("\n--- TOP 15 REKOMENDACJI ---")
    print(top_recommendations)
else:
    print("Brak poprawnych gier.")

