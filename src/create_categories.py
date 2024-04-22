import argparse
import gzip
from pathlib import Path

import pandas as pd
from tqdm import tqdm

import src.fileio as fileio


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


def save_as_gzipped_jsonl(df: pd.DataFrame, prefix: str):
    # Create a subfolder in local_data with the name {prefix}
    path = Path("local_data") / prefix
    path.mkdir(parents=True, exist_ok=True)

    # Save DataFrame as JSON Lines
    df.to_json(path / "test.jsonl", orient="records", lines=True)

    # Gzip the JSON Lines file
    with (path / "test.jsonl").open("rb") as f_in, gzip.open(
        path / "test.jsonl.gz",
        "wb",
    ) as f_out:
        f_out.writelines(f_in)

    # Remove the original JSON Lines file
    (path / "test.jsonl").unlink()


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


def create_dataset(prefix: str, n_articles: int = 5000, n_turns: int = 30):
    parents = clean_parents(pd.read_csv(f"local_data/{prefix}wiki-all-parents.csv"))
    wiki = fileio.read_json(
        fileio.find_latest_file(Path("local_data"), f"{prefix}wiki-sample-*.json"),
    )
    catdf = get_categories(wiki)
    clean_cats = catdf.merge(parents, left_on="categories", right_on="child")[
        ["index", "parent"]
    ].rename(columns={"index": "title", "parent": "category"})
    sample_df = generate_samples(
        wiki,
        clean_cats,
        n_turns=n_turns,
        n_articles=n_articles,
    )

    save_as_gzipped_jsonl(sample_df, prefix)


def main(args: argparse.Namespace):
    for prefix in tqdm(args.prefixes, desc="Languages"):
        create_dataset(prefix, n_articles=args.n_articles, n_turns=args.n_turns)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate sentence/label samples from a wikipedia pipeline",
    )
    parser.add_argument(
        "--n-articles",
        type=int,
        default=512,
    )
    parser.add_argument(
        "--n-turns",
        type=int,
        default=10,
    )
    parser.add_argument(
        "--prefixes",
        nargs="+",
        default=fileio.get_all_prefixes(),
    )
    args = parser.parse_args()
    main(args=args)
