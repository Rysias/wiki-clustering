import bz2
from pathlib import Path

from lxml import etree


def extract_first_article(file_path: Path, num_articles: int = 1) -> None:
    """
    Extracts and prints the title and text of the first article in a Wikimedia XML dump.

    Args:
    file_path (str): The path to the bz2-compressed XML file of Wikimedia articles.
    num_articles (int): The number of articles to extract. Defaults to 1.

    """
    # Open the bz2 file
    articles = []
    with bz2.open(file_path, "rb") as file:
        context = etree.iterparse(
            file,
            events=("end",),
            tag="{http://www.mediawiki.org/xml/export-0.10/}page",
        )
        article_count = 0

        # Process the XML file iteratively
        for event, elem in context:
            if article_count >= num_articles:
                break  # Stop after collecting enough articles

            title = elem.find(".//{http://www.mediawiki.org/xml/export-0.10/}title")
            if not title.text.startswith("Kategori:"):
                continue

            text = elem.find(".//{http://www.mediawiki.org/xml/export-0.10/}text")
            if title is not None and text is not None:
                articles.append(f"Title: {title.text}\nText: {text.text}")
                article_count += 1

            # Clear the element to free up memory
            elem.clear()

    return articles


# Example usage
if __name__ == "__main__":
    path_to_file = Path("local_data/dawiki-20240401-pages-articles.xml.bz2")
    articles = extract_first_article(path_to_file, num_articles=1)
    print(articles)
