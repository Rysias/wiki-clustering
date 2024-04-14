import json
from datetime import datetime
from pathlib import Path

import pandas as pd
from tqdm import tqdm


def read_json(file_path: Path) -> dict:
    return json.loads(file_path.read_text(encoding="utf-8"))


def get_latest_file(directory: Path, pattern: str) -> Path:
    """Get the latest file in a directory that matches the given pattern."""
    files = directory.glob(pattern)
    return max(files, key=lambda f: f.stat().st_mtime)


def misinterpret(text: str, false_encoding: str = "latin1") -> str:
    return text.encode("utf-8").decode(false_encoding)


def clean_dawiki_cats(cats: pd.Series) -> pd.Series:
    return cats.str.replace("|", "").str.strip().apply(misinterpret)


def clean_parents(df: pd.DataFrame) -> pd.DataFrame:
    """Remove the quotes from the parent and child columns."""
    dfcopy = df.copy()
    dfcopy["parent"] = dfcopy["parent"].str.replace("'", "")
    dfcopy["child"] = dfcopy["child"].str.replace("'", "")
    return dfcopy


def generate_samples(
    dawiki: dict[str, tuple[str, list]],
    clean_cats: pd.DataFrame,
    n_turns: int = 30,
    n_articles: int = 5000,
) -> pd.DataFrame:
    all_sentences = []
    all_labels = []
    for _ in tqdm(range(n_turns)):
        sampled_articles = clean_cats.sample(n=n_articles, replace=False)
        texts = [dawiki[title][0] for title in sampled_articles["title"]]
        categories = sampled_articles["category"].tolist()
        all_sentences.append(texts)
        all_labels.append(categories)
    sample_df = pd.DataFrame({"sentences": all_sentences, "labels": all_labels})
    assert (
        sample_df.shape[0] == n_turns
    ), f"Expected {n_turns} but got {sample_df.shape[0]}"
    return sample_df


def get_categories(dawiki: dict[str, tuple[str, list]]) -> pd.DataFrame:
    catdf = (
        pd.DataFrame.from_dict(dawiki, orient="index", columns=["text", "categories"])
        .reset_index()[["index", "categories"]]
        .explode("categories")
        .dropna()
    )
    catdf["categories"] = clean_dawiki_cats(catdf["categories"])
    return catdf


# filter to have value counts of 1 or 2
def filter_cats(clean_cats: pd.DataFrame, max_cats: int = 1) -> pd.DataFrame:
    value_counts = clean_cats["title"].value_counts()
    return clean_cats[
        clean_cats["title"].isin(value_counts[value_counts == max_cats].index)
    ]


def main():
    parents = clean_parents(pd.read_csv("local_data/dawiki-all-parents.csv"))
    dawiki = read_json(
        get_latest_file(Path("local_data"), "dawiki-sample-300000-*.json"),
    )
    catdf = get_categories(dawiki)
    clean_cats = catdf.merge(parents, left_on="categories", right_on="child")[
        ["index", "parent"]
    ].rename(columns={"index": "title", "parent": "category"})
    sample_df = generate_samples(dawiki, clean_cats)

    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    sample_df.to_csv(f"local_data/dawiki-samples-{current_time}.csv")


if __name__ == "__main__":
    main()
