import requests
from bs4 import BeautifulSoup


def fetch_html(url: str) -> str:
    """Fetch the HTML content of a webpage."""
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.text


def parse_data_ct_titles(html_content: str) -> list[str]:
    """Parse and extract all `data-ct-title` attribute values from the given HTML."""
    soup = BeautifulSoup(html_content, "html.parser")
    elements = soup.find_all(attrs={"data-ct-title": True})
    titles = [element["data-ct-title"] for element in elements]
    return titles


def get_top_categories() -> list[str]:
    CATEGORY_URL = "https://da.wikipedia.org/wiki/Kategori:Topniveau_for_emner"
    html = fetch_html(CATEGORY_URL)
    return parse_data_ct_titles(html)


if __name__ == "__main__":
    top_categories = get_top_categories()
    print(top_categories)
