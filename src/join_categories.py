from pathlib import Path

import pandas as pd

import src.get_top_categories as gtc

DATA_PATH = Path("local_data/dawiki-latest-categorylinks.csv")
assert (
    DATA_PATH.exists()
), "The data file is missing. Please download it from the course page."

links = pd.read_csv(DATA_PATH)
ids = pd.read_csv("local_data/dawiki-category-ids.csv")

ids

top_categories = gtc.get_top_categories()


joined = links.merge(ids, left_on="cl_to", right_on="cat_title", how="inner")[
    ["cl_from", "cat_id"]
].rename(columns={"cl_from": "source", "cat_id": "target"})

joined
