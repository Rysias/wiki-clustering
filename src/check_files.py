import numpy as np
import pandas as pd

import src.fileio as fileio


def calculate_n_samples(df: pd.DataFrame) -> int:
    """
    Calculate the number of samples in the dataset.

    Args:
        df (pd.DataFrame): The DataFrame containing the dataset.

    Returns:
        int: The number of samples in the dataset.
    """
    return sum(len(dat) for dat in df["sentences"])


def calculate_avg_character_length(df: pd.DataFrame) -> float:
    """
    Calculate the average character length of the articles.

    Args:
        df (pd.DataFrame): The DataFrame containing the dataset.

    Returns:
        float: The average character length of the articles.
    """
    sentence_lenghts = [
        len(sentence) for sentences in df["sentences"] for sentence in sentences
    ]
    return np.mean(sentence_lenghts)


if __name__ == "__main__":
    for prefix in ["sq", "da", "lv", "gv"]:
        print(f"Reading {prefix}")
        df = fileio.read_gzipped_jsonl(prefix)
        print(df["sentences"][0][0])
        print(f"Number of samples: {calculate_n_samples(df)}")
        print(f"Average character length: {calculate_avg_character_length(df)}")
