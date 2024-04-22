from pathlib import Path

import requests
from loguru import logger
from tqdm import tqdm

import src.fileio as fileio

DOWNLOAD_URL = "https://dumps.wikimedia.org/{prefix}wiki/latest/"
SAVE_DIR = Path("local_data")
DOWNLOAD_PATTERNS = [
    "{prefix}wiki-latest-categorylinks.sql.gz",
    "{prefix}wiki-latest-page.sql.gz",
    "{prefix}wiki-latest-pages-articles.xml.bz2",
]


def download_file(url: str, path: Path) -> None:
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        total_size = int(response.headers.get("content-length", 0))
        with path.open("wb") as file, tqdm(
            total=total_size,
            unit="B",
            unit_scale=True,
            desc=f"Downloading {path.name}",
        ) as progress:
            for chunk in response.iter_content(chunk_size=8192):
                progress.update(len(chunk))
                file.write(chunk)


def download_wikidump(prefix: str) -> None:
    for pattern in DOWNLOAD_PATTERNS:
        logger.info(f"Downloading {pattern.format(prefix=prefix)}")
        path = SAVE_DIR / pattern.format(prefix=prefix)
        if path.exists():
            logger.info(f"File {path.name} already exists. Skipping download.")
            continue
        url = DOWNLOAD_URL.format(prefix=prefix) + pattern.format(prefix=prefix)
        download_file(url, path)
        logger.info(f"Downloaded {path.name}")


def main() -> None:
    for prefix in tqdm(fileio.get_all_prefixes(), desc="Downloading dumps"):
        download_wikidump(prefix)


if __name__ == "__main__":
    main()
