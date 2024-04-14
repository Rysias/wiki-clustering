import json
from pathlib import Path


def read_json(path: Path | str) -> dict:
    readpath = path
    if isinstance(readpath, str):
        readpath = Path(readpath)
    return json.loads(readpath.read_text(encoding="utf-8"))


def find_latest_file(directory: Path, pattern: str) -> Path:
    """Find the latest file in a directory that matches the given pattern."""
    files = directory.glob(pattern)
    return max(files, key=lambda f: f.stat().st_mtime)
