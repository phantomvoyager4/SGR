import os
import sys
import glob
from vectorization_script import process_pipeline

# Grab all the chunk files relative to where the script is located
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
data_path = os.path.join(base_dir, 'data', 'games_informations', '*.jsonl')
jsonl_path = glob.glob(data_path)

if not jsonl_path:
    print(f"[ERROR] Source files not found for path: {jsonl_path}")
    sys.exit(1)

print(f"[INFO] Target files verified: {len(jsonl_path)} files found.")

# Phase 1: Data Loading
print(f"[INFO] Source files: {jsonl_path}")

# Phase 2: Pipeline Execution
try:
    print("[INFO] Executing processing pipeline...")
    massive_df = process_pipeline(jsonl_path)

    if massive_df is None or massive_df.empty:
        print("[WARNING] Pipeline returned an empty DataFrame.")
    else:
        print(f"[INFO] Pipeline complete. Final dataset shape: {massive_df.shape}")
        excel_path = os.path.join(base_dir, 'data', 'parquet_example', 'index_table.xlsx')
        os.makedirs(os.path.dirname(excel_path), exist_ok=True)
        index_df = massive_df['name']
        index_df['index'] = index_df.index
        index_df.to_excel(excel_path)

except Exception as e:
    print(f"[ERROR - PIPELINE] Processing failed inside process_pipeline. Details: {e}")
    sys.exit(1)

# Phase 3: Data Export
try:
    print("Saving to Parquet...")
    output_path = os.path.join(base_dir, 'data', 'parquet_example', 'games_fully_vectorized.parquet')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    # Reset index so 'name' becomes a standard column before saving, maintaining it without relying on index logic
    massive_df.reset_index().to_parquet(output_path, engine='pyarrow', index=False)
    print(f"[INFO] Process complete. Saved to: {output_path}")
except ImportError as e:
    print(f"[ERROR - DEPENDENCY] Missing Parquet engine. Run 'pip install pyarrow'. Details: {e}")
    sys.exit(1)
except OSError as e:
    print(f"[ERROR - I/O WRITE] OS rejected file write (Check permissions/locks). Details: {e}")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR - EXPORT] Unexpected failure during Parquet save. Details: {e}")
    sys.exit(1)