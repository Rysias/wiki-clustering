import gzip
import json
from pathlib import Path

import pandas as pd

CONFIG_DIR = Path("language_configs")


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


def find_latest_file(directory: Path, pattern: str) -> Path | None:
    """Find the latest file in a directory that matches the given pattern."""
    files = list(directory.glob(pattern))
    if not files:
        return None
    return max(files, key=lambda f: f.stat().st_mtime)


def get_prefix(file: Path) -> str:
    return file.stem.split("-")[0]


def get_all_prefixes() -> list[str]:
    return [get_prefix(conffile) for conffile in CONFIG_DIR.glob("*.json")]
