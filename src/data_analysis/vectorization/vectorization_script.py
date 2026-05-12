import json
import re
import pandas as pd
import os

from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from nltk.stem import WordNetLemmatizer

current_dir = os.path.dirname(os.path.abspath(__file__))
settings_path = os.path.join(current_dir, "settings.json")

settings = pd.read_json(settings_path, typ="series")


def data_load(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            item = json.loads(line)
            appid, info = next(iter(item.items()))
            info['appid'] = appid
            data.append(info)
    return data


def df_cleansing(data_to_df):
    df = pd.DataFrame(data_to_df)
    
    # 0. Filter non-English games early using 'supported_languages'
    if 'supported_languages' in df.columns:
        df = df[df['supported_languages'].str.contains('English', case=False, na=False)]
    
    # 1. Drop columns in one vectorized operation without loops
    cols_to_drop = ['header_image', 'reviews', 'supported_languages', 'support_info', 'game_link', 'appid', 'demos', 'ext_user_account_notice', 'drm_notice']
    df = df.drop(columns=cols_to_drop, errors='ignore')

    # 2. Use pure pandas .str.replace chain
    pattern = r'<[^>]*>'
    df['about_the_game'] = df['about_the_game'].str.replace(pattern, ' ', regex=True).str.replace(r'\n', ' ', regex=True)

    # 3. Clean to lists.
    def clean_list(x):
        return [str(i).strip() for i in x if str(i).strip()] if isinstance(x, list) else []

    def clean_dict_list(x):
        return [d.get('description', '').strip() for d in x if d.get('description', '').strip()] if isinstance(x, list) else []

    df['developers'] = df['developers'].apply(clean_list)
    df['publishers'] = df['publishers'].apply(clean_list)
    df['genres'] = df['genres'].apply(clean_dict_list)
    df['categories'] = df['categories'].apply(clean_dict_list)

    df = df.reset_index(drop=True)

    # 4. Vectorized boolean mapping
    df['is_free'] = (df['is_free'] == True).astype(int)

    # 5. Extract MultiLabelBinarizer results in memory and concat once
    def get_mlb_df(column_name):
        mlb = MultiLabelBinarizer()
        encoded_matrix = mlb.fit_transform(df[column_name])
        # Add column prefix to prevent duplicate names like 'EckGames' appearing in both developer and publisher
        return pd.DataFrame(encoded_matrix, columns=[f"{column_name}_{str(c)}" for c in mlb.classes_], index=df.index)

    mlb_dfs = [
        get_mlb_df('genres'),
        get_mlb_df('categories'),
        get_mlb_df('developers'),
        get_mlb_df('publishers')
    ]
    
    # Drop original categorical columns
    df = df.drop(columns=['genres', 'categories', 'developers', 'publishers'])
    
    df = pd.concat([df] + mlb_dfs, axis=1)
    
    df = df.drop(columns=['Free To Play'], errors='ignore')

    def delete_irrelevant_column(columnname, df, count):
        prefix = f"{columnname}_"
        target_cols = df.filter(like=prefix).columns
        
        if len(target_cols) > count:
            # Vectorized sum for all target columns at once
            col_sums = df[target_cols].sum()
            
            # Identify the top 'count' columns with the highest sums
            cols_to_keep = col_sums.nlargest(count).index
            cols_to_drop = set(target_cols) - set(cols_to_keep)
            
            # Drop the irrelevant columns in one fast operation
            df.drop(columns=list(cols_to_drop), inplace=True)

    delete_irrelevant_column('developers', df, settings['max_developers'])
    delete_irrelevant_column('publishers', df, settings['max_publishers'])


    df['dlc_count'] = df['dlc'].apply(lambda x: len(x) if isinstance(x, list) else 0)
    df['achievements_count'] = df['achievements'].apply(lambda x: x.get('total', 0) if isinstance(x, dict) else 0)
    df = df.drop(columns=['dlc', 'achievements'], errors='ignore')

    # 6. Vectorized datetime parsing
    release_str = df['release_date'].apply(lambda x: x.get('date', '') if isinstance(x, dict) else '')
    df['release_year'] = pd.to_datetime(release_str, errors='coerce').dt.year
    df = df.drop(columns=['release_date'], errors='ignore')

    if 'controller_support' in df.columns:
        df['controller_support'] = df['controller_support'].fillna('0').astype(str).str.replace('full', '1')

    if 'recommendations' in df.columns:
        df['recommendations'] = df['recommendations'].apply(lambda x: x.get('total', 0) if isinstance(x, dict) else 0)
    
    df['price_overview'] = df['price_overview'].apply(lambda x: float(x.get('initial', 0)) if isinstance(x, dict) else 0.0)
    
    return df


def nlp_part(dataframe):
    about = dataframe['about_the_game'].astype(str)

    lemmatizer = WordNetLemmatizer()
    data_clean = []
    for cell in about:
        cell = cell.lower()
        tokens = re.findall(r'\b[a-z0-9\-]+\b', cell)
        cell_clean = ' '.join(lemmatizer.lemmatize(word) for word in tokens)
        data_clean.append(cell_clean)

    tfidf = TfidfVectorizer(stop_words='english', max_features=settings['max_features'], min_df=10, max_df=0.85)
    data_tfidf = tfidf.fit_transform(data_clean)

    df_tfidf = pd.DataFrame(
        data_tfidf.toarray(), 
        columns=[f"nlp_{str(c)}" for c in tfidf.get_feature_names_out()],
        index=dataframe.index
    )

    dataframe_final = pd.concat([dataframe.drop('about_the_game', axis=1, errors='ignore'), df_tfidf], axis=1)

    return dataframe_final


def scaling(df):
    cols_to_scale = ['price_overview', 'recommendations', 'dlc_count', 'achievements_count']

    scaler = MinMaxScaler()

    def scale(dataframe, column):
        dataframe[column] = scaler.fit_transform(dataframe[[column]])

    for col in cols_to_scale:
        scale(df, col)  

    return df


def process_pipeline(file_paths):
    """
    Runs the entire pipeline from loading data to vectorizing and scaling it.
    Can accept a single file path (string) or a list of file paths.
    """
    if isinstance(file_paths, str):
        file_paths = [file_paths]
        
    all_data = []
    for file_path in file_paths:
        print(f"Loading {file_path}...")
        all_data.extend(data_load(file_path))
        
    print(f"Total games loaded: {len(all_data)}")
    print("Cleaning data and extracting categories...")
    df = df_cleansing(all_data)
    df = df.set_index('name')
    
    print("Running NLP TF-IDF...")
    df_nlp = nlp_part(df)
    
    print("Scaling values...")
    df_scaled = scaling(df_nlp)
    
    # Fill remaining NaNs with 0 before algorithm feeding
    df_scaled = df_scaled.fillna(0)
    
    # Ensure all column names are strictly strings without duplicates for Parquet compatibility
    df_scaled.columns = df_scaled.columns.astype(str)
    
    print("Pipeline complete!")
    
    return df_scaled 