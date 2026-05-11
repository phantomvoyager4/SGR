import glob
import os
from vectorization_script import process_pipeline

# Grab all the chunk files relative to where the script is located
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
data_path = os.path.join(base_dir, 'data', 'games_informations', '*.jsonl')
all_chunks = glob.glob(data_path)

if not all_chunks:
    print(f"Error: No chunk files found at {data_path} ! Check your file paths.")
    exit()

print(f"Found {len(all_chunks)} chunks to process.")
print("Starting the grand pipeline...")
massive_df = process_pipeline(all_chunks)

print(f"Final dataset shape: {massive_df.shape}")

print("Saving to Parquet...")
output_path = os.path.join(base_dir, 'data', 'games_fully_vectorized.parquet')
massive_df.to_parquet(output_path, engine='pyarrow')
print("Done!")