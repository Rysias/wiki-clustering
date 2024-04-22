import argparse
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from src.config import Config


def get_all_parents(
    joined: pd.DataFrame,
    top_level: pd.Series,
    num_levels: int = 20,
) -> pd.DataFrame:
    parent_list = []
    new_parents = joined[joined["parent"].isin(top_level)]
    orphans = joined[
        ~joined["parent"].isin(top_level) & ~joined["child"].isin(top_level)
    ]
    for i in tqdm(range(num_levels)):
        parent_list.append(new_parents)
        new_parents = (
            orphans.merge(new_parents, how="left", left_on="parent", right_on="child")
            .rename(columns={"child_x": "child", "parent_y": "parent"})[
                ["child", "parent"]
            ]
            .dropna()
        )
        orphans = orphans[~orphans["child"].isin(new_parents["child"])]
    all_parents = pd.concat(parent_list).drop_duplicates().reset_index(drop=True)
    return all_parents


def main(args: argparse.Namespace):
    config: Config = Config.from_json(args.config_path)
    prefix = config.prefix
    ids = pd.read_csv(f"local_data/{prefix}wiki-category-ids.csv")
    links = pd.read_csv(f"local_data/{prefix}wiki-latest-categorylinks.csv")
    joined = links.merge(ids, left_on="cl_from", right_on="cat_id").rename(
        columns={"cat_title": "child", "cl_to": "parent"},
    )[["child", "parent"]]
    top_level = joined.loc[joined["parent"] == config.top_level, "child"].values

    all_parents = get_all_parents(joined, top_level)
    all_parents.to_csv(f"local_data/{prefix}wiki-all-parents.csv", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Join categories with their parents.",
    )
    parser.add_argument(
        "--config-path",
        type=Path,
        default=Path("da-config.json"),
    )
    args = parser.parse_args()
    main(args=args)
