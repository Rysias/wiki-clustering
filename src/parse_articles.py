import argparse
import bz2
import json
import re
from datetime import datetime
from pathlib import Path

from loguru import logger
from lxml import etree

import src.fileio as fileio
from src.config import Config


def clean_text_generic(text: str, start_str: str, end_str: str) -> str:
    """
    Cleans the article text by removing unwanted sections.

    Args:
        text (str): The raw text from the Wikimedia article.
        start_str (str): The string that marks the start of an unwanted section.
        end_str (str): The string that marks the end of an unwanted section.

    Returns:
        str: The cleaned text.
    """
    cleaned_text = ""
    i = 0
    while i < len(text):
        start_index = text.find(start_str, i)

        if start_index == -1:
            cleaned_text += text[i:]
            break

        # Append text up to the start of the unwanted section
        cleaned_text += text[i:start_index]

        # Now find the corresponding closing brackets starting from just after start_str
        count = len(
            end_str,
        )  # Starts after encountering start_str which opens the unwanted section
        j = start_index + len(start_str)  # Start searching after start_str
        while j < len(text) and count > 0:
            if text[j : j + len(start_str)] == start_str:
                count += len(start_str)
                j += len(start_str)  # Move past the found start_str
            elif text[j : j + len(end_str)] == end_str:
                count -= len(end_str)
                j += len(end_str)  # Move past the found end_str
            else:
                j += 1

        # Update i to continue after the closed unwanted section
        i = j

    return cleaned_text.strip()


def clean_text(text: str, config: Config | None = None) -> str:
    """
    Cleans the article text by removing bracketed file references that start with 'Fil:'.

    Args:
        text (str): The raw text from the Wikimedia article.
        config (dict): A dictionary with file and infobox strings. Defaults to None.

    Returns:
        str: The cleaned text.
    """
    file = config.file if config else "Fil"
    infobox = config.infobox if config else "Infoboks"
    cleaned = clean_text_generic(text, f"[[{file}:", "]]")
    cleaned = clean_text_generic(
        cleaned,
        "{{Infoboks".replace("Infoboks", infobox),
        "}}",
    )
    return cleaned


def extract_articles(
    file_path: Path,
    num_articles: int = 1,
    config: Config | None = None,
) -> dict[str, tuple[str, list[str]]]:
    """
    Extracts articles from a bz2-compressed Wikimedia XML dump.

    Args:
        file_path (Path): The path to the bz2-compressed XML file.
        num_articles (int): The number of articles to extract. Defaults to 1.
        config (dict[str, str]): A dictionary with start and end strings for unwanted sections. Defaults to None.

    Returns:
        dict[str, tuple[str, list[str]]]: A dictionary with titles as keys and a tuple of cleaned text and categories.
    """
    articles = {}
    with bz2.open(file_path, "rb") as file:
        context = etree.iterparse(
            file,
            events=("end",),
            tag="{http://www.mediawiki.org/xml/export-0.10/}page",
        )
        article_count = 0

        for event, elem in context:
            if article_count >= num_articles:
                break

            title_elem = elem.find(
                ".//{http://www.mediawiki.org/xml/export-0.10/}title",
            )
            if title_elem.text is None or title_elem.text.startswith(config.category):
                continue
            text_elem = elem.find(".//{http://www.mediawiki.org/xml/export-0.10/}text")
            if text_elem.text is None or "#REDIRECT" in text_elem.text:
                continue
            categories = []

            if title_elem is not None and text_elem is not None:
                title = title_elem.text
                raw_text = text_elem.text or ""

                # Clean the text
                cleaned_text = clean_text(raw_text, config=config)
                # only save until the first "\n\n"
                cleaned_text = cleaned_text.split("\n\n")[0]

                # Extract categories, assuming categories are mentioned as links or in a specific section
                categories = re.findall(
                    rf"\[\[{config.category}:(.*?)\]\]",
                    raw_text,
                )

                articles[title] = (cleaned_text, categories)
                article_count += 1

            elem.clear()  # Free memory by clearing the element
    return articles


def main(args: argparse.Namespace):
    N = args.num_articles
    CONFIG_PATH = args.config_path
    assert CONFIG_PATH.exists(), f"Config file not found at {CONFIG_PATH}"
    config: Config = Config.from_json(CONFIG_PATH)
    if args.skip_if_exists:
        path_to_file = fileio.find_latest_file(
            Path("local_data"),
            f"{config.prefix}wiki-sample-{N}-*.json",
        )
        if path_to_file is not None:
            logger.info(f"File {path_to_file} already exists. Skipping extraction.")
            return

    path_to_file = fileio.find_latest_file(
        Path("local_data"),
        f"{config.prefix}wiki-*-pages-articles.xml.bz2",
    )
    logger.info(f"Extracting {N} articles from {path_to_file}")
    articles = extract_articles(path_to_file, num_articles=N, config=config)
    SAVE_PATH = Path(
        f"local_data/{config.prefix}wiki-sample-{N}-{datetime.now().strftime('%Y%m%d%H%M%S')}.json",
    )
    logger.info(f"Saving articles to {SAVE_PATH}")
    SAVE_PATH.write_text(
        json.dumps(articles, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("Done parsing articles!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract articles from a Wikimedia XML dump.",
    )
    parser.add_argument(
        "--num-articles",
        type=int,
        default=1,
        help="The number of articles to extract. Defaults to 1.",
    )
    parser.add_argument(
        "--config-path",
        type=Path,
        default=Path("da-config.json"),
    )
    parser.add_argument(
        "--skip-if-exists",
        action="store_true",
        help="Skip extraction if a file with the same name already exists.",
    )
    args = parser.parse_args()
    main(args)
