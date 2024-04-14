import gzip
import json
from pathlib import Path

import pandas as pd


def read_gzipped_jsonl(prefix: str) -> pd.DataFrame:
    # Define the path to the gzipped JSON Lines file
    path = Path("local_data") / prefix / "test.jsonl.gz"

    # Open the gzipped JSON Lines file and read it into a DataFrame
    with gzip.open(path, "rb") as f:
        df = pd.read_json(f, lines=True)

    return df


def read_json(path: Path | str) -> dict:
    readpath = path
    if isinstance(readpath, str):
        readpath = Path(readpath)
    return json.loads(readpath.read_text(encoding="utf-8"))


def find_latest_file(directory: Path, pattern: str) -> Path:
    """Find the latest file in a directory that matches the given pattern."""
    files = directory.glob(pattern)
    return max(files, key=lambda f: f.stat().st_mtime)
