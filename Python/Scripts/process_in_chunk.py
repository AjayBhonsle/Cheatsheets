import pandas as pd


def transform_chunk(chunk: pd.DataFrame) -> pd.DataFrame:
    """Apply a simple transformation to each chunk."""
    chunk = chunk.copy()
    chunk.columns = [str(col).strip().lower() for col in chunk.columns]

    for col in chunk.select_dtypes(include=["object"]).columns:
        chunk[col] = chunk[col].astype(str).str.strip()

    return chunk


def read_large_file_in_chunks(
    file_path: str,
    chunksize: int = 100000,
    delimiter: str = ",",
    encoding: str = "utf-8",
) -> pd.DataFrame:
    """Read a large file in chunks and build a DataFrame."""
    chunks = []

    for chunk in pd.read_csv(file_path, sep=delimiter, encoding=encoding, chunksize=chunksize):
        chunks.append(transform_chunk(chunk))

    if not chunks:
        return pd.DataFrame()

    return pd.concat(chunks, ignore_index=True)

df = read_large_file_in_chunks(
    'Python\Scripts\LargeFileProcessing\processed_output.csv',
    chunksize= 100000,
    delimiter=',',
    encoding='utf-8',
)

print(f"Loaded {len(df)} rows into a DataFrame")
print(df.head())

