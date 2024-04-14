import pandas as pd
from tqdm import tqdm


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


if __name__ == "__main__":
    ids = pd.read_csv("local_data/dawiki-category-ids.csv")
    links = pd.read_csv("local_data/dawiki-latest-categorylinks.csv")
    BAD_CATEGORIES = ["'Skjulte_kategorier'"]
    ids = ids[~ids["cat_title"].isin(BAD_CATEGORIES)]
    links = links[~links["cl_to"].isin(BAD_CATEGORIES)]

    joined = links.merge(ids, left_on="cl_from", right_on="cat_id").rename(
        columns={"cat_title": "child", "cl_to": "parent"},
    )[["child", "parent"]]
    top_level = joined.loc[joined["parent"] == "'Topniveau_for_emner'", "child"].values

    all_parents = get_all_parents(joined, top_level)
    all_parents.to_csv("local_data/dawiki-all-parents.csv", index=False)
