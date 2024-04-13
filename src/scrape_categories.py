import asyncio
import json
from pathlib import Path
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from loguru import logger

# Global constants
BASE_URL = "https://da.wikipedia.org"
PROCESSED_URLS: set[str] = set()


async def fetch_subcategories(
    session: httpx.AsyncClient,
    category_url: str,
) -> dict[str, dict]:
    """Fetch all subcategories for a given category URL."""
    subcategories: dict[str, dict] = {}
    try:
        response = await session.get(category_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for link in soup.select("div.CategoryTreeItem a"):
            if "Kategori:" in link.get("title", ""):
                subcat_url = urljoin(BASE_URL, link["href"])
                subcategories[subcat_url] = {}
        logger.debug(
            f"Subcategories found at {category_url}: {list(subcategories.keys())}",
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"Request failed at {category_url}: {e}")
    return subcategories


async def build_category_tree(
    session: httpx.AsyncClient,
    category_url: str,
    tree: dict[str, dict],
):
    """Recursively build the tree of categories."""
    if category_url in PROCESSED_URLS:
        logger.debug(f"Skipping already processed category: {category_url}")
        return

    PROCESSED_URLS.add(category_url)
    logger.info(f"Processing category: {category_url}")
    subcategories = await fetch_subcategories(session, category_url)
    tree[category_url] = subcategories

    for subcat_url in subcategories:
        await asyncio.sleep(0.5)  # Mild rate limiting
        await build_category_tree(session, subcat_url, tree[category_url])


def save_tree_to_file(
    tree: dict[str, dict],
    filename: Path = Path("category_tree.json"),
):
    """Save the category tree to a JSON file."""
    with filename.open("w", encoding="utf-8") as file:
        json.dump(tree, file, ensure_ascii=False, indent=4)
    logger.info(f"Category tree saved to {filename}")


async def main():
    start_url = "https://da.wikipedia.org/wiki/Kategori:Topniveau_for_emner"
    category_tree: dict[str, dict] = {}
    async with httpx.AsyncClient(http2=True) as session:
        await build_category_tree(session, start_url, category_tree)
    save_tree_to_file(category_tree)


if __name__ == "__main__":
    asyncio.run(main())
