import bz2
import json
import re
from datetime import datetime
from pathlib import Path

from lxml import etree


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


def clean_text(text: str) -> str:
    """
    Cleans the article text by removing bracketed file references that start with 'Fil:'.

    Args:
        text (str): The raw text from the Wikimedia article.

    Returns:
        str: The cleaned text.
    """
    cleaned = clean_text_generic(text, "[[Fil:", "]]")
    cleaned = clean_text_generic(cleaned, "{{Infoboks:", "}}")
    return cleaned


def extract_articles(
    file_path: Path,
    num_articles: int = 1,
) -> dict[str, tuple[str, list[str]]]:
    """
    Extracts articles from a bz2-compressed Wikimedia XML dump.

    Args:
        file_path (Path): The path to the bz2-compressed XML file.
        num_articles (int): The number of articles to extract. Defaults to 1.

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
            if title_elem.text is None or title_elem.text.startswith("Kategori:"):
                continue
            text_elem = elem.find(".//{http://www.mediawiki.org/xml/export-0.10/}text")
            if text_elem.text is None or "#REDIRECT" in text_elem.text:
                continue
            categories = []

            if title_elem is not None and text_elem is not None:
                title = title_elem.text
                raw_text = text_elem.text or ""

                # Clean the text
                cleaned_text = clean_text(raw_text)
                # only save until the first "\n\n"
                cleaned_text = cleaned_text.split("\n\n")[0]

                # Extract categories, assuming categories are mentioned as links or in a specific section
                categories = re.findall(r"\[\[Kategori:(.*?)\]\]", raw_text)

                articles[title] = (cleaned_text, categories)
                article_count += 1

            elem.clear()  # Free memory by clearing the element
    return articles


if __name__ == "__main__":
    N = 300_000
    path_to_file = Path("local_data/dawiki-20240401-pages-articles.xml.bz2")
    articles = extract_articles(path_to_file, num_articles=N)
    SAVE_PATH = Path(
        f"local_data/dawiki-sample-{N}-{datetime.now().strftime('%Y%m%d%H%M%S')}.json",
    )
    SAVE_PATH.write_text(
        json.dumps(articles, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
