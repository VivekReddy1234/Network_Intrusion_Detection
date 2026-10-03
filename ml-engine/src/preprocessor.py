import pandas as pd
import numpy as np
import json
import os
from sklearn.model_selection import train_test_split


# Columns confirmed to produce inf values in CIC-IDS-2017
INF_COLS = ['Flow Bytes/s', 'Flow Packets/s']

# Near-zero variance columns — confirmed from EDA, safe to drop
LOW_VAR_COLS = [
    'Bwd PSH Flags',
    'Bwd URG Flags',
    'Fwd Avg Bytes/Bulk',
    'Fwd Avg Packets/Bulk',
    'Fwd Avg Bulk Rate',
    'Bwd Avg Bytes/Bulk',
    'Bwd Avg Packets/Bulk',
    'Bwd Avg Bulk Rate',
]

# Full label → integer mapping for multiclass
MULTICLASS_MAP = {
    'BENIGN'                         : 0,
    'DoS Hulk'                       : 1,
    'PortScan'                       : 2,
    'DDoS'                           : 3,
    'DoS GoldenEye'                  : 4,
    'FTP-Patator'                    : 5,
    'SSH-Patator'                    : 6,
    'DoS slowloris'                  : 7,
    'DoS Slowhttptest'               : 8,
    'Bot'                            : 9,
    'Web Attack – Brute Force'       : 10,
    'Web Attack – XSS'               : 11,
    'Infiltration'                   : 12,
    'Web Attack – Sql Injection'     : 13,
    'Heartbleed'                     : 14,
}



def load_and_clean(path: str, sample_frac: float = 1.0) -> pd.DataFrame:
    print(f'  Loading {os.path.basename(path)}...')

    df = pd.read_csv(path, low_memory=False)
    df.columns = df.columns.str.strip()
    df.replace([np.inf, -np.inf], np.nan, inplace=True)

    rows_before = len(df)
    df.dropna(inplace=True)
    rows_dropped = rows_before - len(df)
    if rows_dropped > 0:
        print(f'    Dropped {rows_dropped:,} rows with NaN/inf')

    # Optional: sample for faster dev iteration
    if sample_frac < 1.0:
        df = df.sample(frac=sample_frac, random_state=42)
        print(f'    Sampled {sample_frac*100:.0f}% → {len(df):,} rows')

    return df


def load_all_csvs(data_dir: str, sample_frac: float = 1.0) -> pd.DataFrame:
    csv_files = [
        os.path.join(data_dir, f)
        for f in os.listdir(data_dir)
        if f.endswith('.csv') and f != 'cleaned.csv'
    ]

    if not csv_files:
        raise FileNotFoundError(f'No CSV files found in {data_dir}')

    print(f'Found {len(csv_files)} CSV files. Loading...')
    dfs = [load_and_clean(f, sample_frac) for f in csv_files]

    df = pd.concat(dfs, ignore_index=True)
    print(f'\nMerged shape: {df.shape}')
    return df


def load_cleaned_csv(path: str) -> pd.DataFrame:
    """
    Load the pre-cleaned CSV saved by the EDA notebook.
    Faster than re-loading all raw CSVs — use this in train.py.
    """
    print(f'Loading cleaned dataset from {path}...')
    df = pd.read_csv(path, low_memory=False)

    df.columns = df.columns.str.strip()
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)

    print(f'Loaded: {df.shape}')
    return df


# Feature engineering

def drop_low_variance(df: pd.DataFrame, cols: list = LOW_VAR_COLS) -> pd.DataFrame:
    cols_to_drop = [c for c in cols if c in df.columns]
    df = df.drop(columns=cols_to_drop)
    print(f'Dropped {len(cols_to_drop)} low-variance columns')
    return df


def get_feature_columns(df: pd.DataFrame) -> list:
    exclude = ['Label', 'source_file', 'binary_label']
    return [c for c in df.columns if c not in exclude]


# Label encoding 

def encode_binary(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['binary_label'] = (df['Label'] != 'BENIGN').astype(int)
    return df


def encode_multiclass(df: pd.DataFrame,
                       label_map: dict = MULTICLASS_MAP) -> pd.DataFrame:
    df = df.copy()
    df['Label'] = df['Label'].str.strip()

    df['multi_label'] = df['Label'].map(label_map)

    unknown = df['multi_label'].isna().sum()
    if unknown > 0:
        print(f'Warning: {unknown:,} rows have unknown labels → mapped to -1')
        print(f"Unknown labels: {df[df['multi_label'].isna()]['Label'].unique()}")
        df['multi_label'] = df['multi_label'].fillna(-1).astype(int)
        # Drop unknowns to avoid polluting training
        df = df[df['multi_label'] != -1]

    df['multi_label'] = df['multi_label'].astype(int)
    return df


def save_label_map(label_map: dict, out_path: str) -> None:
    """Save label map to JSON so the dashboard can display attack names."""
    # Invert the map: int → string (for decoding predictions)
    inv_map = {str(v): k for k, v in label_map.items()}
    with open(out_path, 'w') as f:
        json.dump(inv_map, f, indent=2)
    print(f'Label map saved to {out_path}')


# Train / test split 

def split(df: pd.DataFrame,
          feature_cols: list,
          label_col: str,
          test_size: float = 0.2,
          random_state: int = 42):
    X = df[feature_cols]
    y = df[label_col]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=y       
    )

    print(f'Train: {X_train.shape} | Test: {X_test.shape}')
    print(f'Train label distribution:\n{y_train.value_counts().to_string()}')

    return X_train, X_test, y_train, y_test


# Full pipeline

def run_preprocessing(data_path: str,
                      mode: str = 'binary',
                      sample_frac: float = 1.0,
                      test_size: float = 0.2):
    # Load
    if os.path.isfile(data_path):
        df = load_cleaned_csv(data_path)
    else:
        df = load_all_csvs(data_path, sample_frac)

    if sample_frac < 1.0 and os.path.isfile(data_path):
        df = df.sample(frac=sample_frac, random_state=42)
        print(f'Sampled {sample_frac*100:.0f}% → {len(df):,} rows')

    # Drop low-variance features
    df = drop_low_variance(df)

    # Encode labels
    if mode == 'binary':
        df = encode_binary(df)
        label_col = 'binary_label'
    elif mode == 'multiclass':
        df = encode_multiclass(df)
        label_col = 'multi_label'
    else:
        raise ValueError(f"mode must be 'binary' or 'multiclass', got '{mode}'")

    # Get feature columns
    feature_cols = get_feature_columns(df)

    print(f'\nFeatures: {len(feature_cols)}')
    print(f'Label column: {label_col}')
    print(f'Class distribution:\n{df[label_col].value_counts().to_string()}')

    # Split
    X_train, X_test, y_train, y_test = split(
        df, feature_cols, label_col, test_size
    )

    return X_train, X_test, y_train, y_test, feature_cols


# Quick sanity check

if __name__ == '__main__':
    import sys

    data_path = sys.argv[1] if len(sys.argv) > 1 else '../data/cleaned.csv'

    print('=== Running preprocessor sanity check ===\n')
    X_train, X_test, y_train, y_test, features = run_preprocessing(
        data_path=data_path,
        mode='binary',
        sample_frac=0.1,   # use 10% for quick check
        test_size=0.2
    )

    print('\n=== Results ===')
    print(f'X_train shape : {X_train.shape}')
    print(f'X_test shape  : {X_test.shape}')
    print(f'Features      : {len(features)}')
    print(f'Sample features: {features[:5]}')
    print('\nSanity check passed ✓')