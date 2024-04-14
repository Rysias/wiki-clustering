import argparse
import gzip
from collections.abc import Generator
from pathlib import Path

import pandas as pd
from tqdm import tqdm

import src.fileio as fileio

CATEGORYLINKS_COLS = [
    "cl_from",
    "cl_to",
    "cl_sortkey",
    "cl_timestamp",
    "cl_sortkey_prefix",
    "cl_collation",
    "cl_type",
]


def read_sql_gz(file_path: Path) -> Generator[str]:
    with gzip.open(file_path, "rt", encoding="latin1") as file:
        for line in file:
            if not line.startswith("INSERT INTO"):
                continue
            yield line


def parse_sql_inserts(sql_content: str) -> list[tuple]:
    """Parse SQL INSERT statements from a string to extract data into tuples for DataFrame creation."""
    records = []
    current_record = []
    paren_level = 0
    record = False
    in_string = False
    escape_character = False  # To handle escaping quotes inside strings
    value = ""

    for char in sql_content:
        # Check for escape character
        if char == "\\" and in_string:
            escape_character = not escape_character  # Toggle escape status
            value += char
            continue
        if char == "'" and not escape_character:
            # Toggle the in_string flag if we're not currently escaping
            in_string = not in_string

        if in_string or escape_character:
            # Add characters to value if inside a string
            value += char
            escape_character = False if escape_character else escape_character
            continue

        # Normal parsing outside of strings
        if char == "(":
            if paren_level == 0:
                record = True  # Start of new record
                value = ""
            paren_level += 1
        elif char == ")":
            paren_level -= 1
            if paren_level == 0 and record:
                # Complete the current record
                current_record.append(value.strip())
                records.append(tuple(current_record))
                current_record = []
                record = False  # Reset record flag
            elif record:
                value += char  # Include ')' in the value
        elif char == "," and paren_level == 1:
            current_record.append(value.strip())
            value = ""  # Reset the current field value
        elif record:
            value += char  # Append character to current field value

    return records


def read_inserts(path: Path) -> list[tuple]:
    new_sql_content = read_sql_gz(path)
    all_new_records = []
    for line in tqdm(new_sql_content):
        new_records = parse_sql_inserts(line)
        all_new_records.extend(new_records)
    return all_new_records


def main(args: argparse.Namespace):
    config = fileio.read_json(args.config_path)
    new_path = Path(f"local_data/{config['prefix']}wiki-latest-categorylinks.sql.gz")
    new_real_records = read_inserts(new_path)

    new_df = pd.DataFrame(new_real_records, columns=CATEGORYLINKS_COLS)
    new_df.loc[new_df["cl_type"] == "'subcat'", ["cl_from", "cl_to"]].to_csv(
        f"local_data/{config['prefix']}wiki-latest-categorylinks.csv",
        index=False,
    )

    pagepath = Path(f"local_data/{config['prefix']}wiki-latest-page.sql.gz")
    pages = read_inserts(pagepath)

    CATEGORYSPACE = "14"
    columns = ["cat_id", "cat_title"]
    cats = [(record[0], record[2]) for record in pages if record[1] == CATEGORYSPACE]
    catdf = pd.DataFrame(cats, columns=columns)
    catdf.to_csv(f"local_data/{config['prefix']}wiki-category-ids.csv", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parse SQL GZ files to extract category links and pages",
    )
    parser.add_argument(
        "--config-path",
        type=Path,
        default=Path("da-config.json"),
    )
    args = parser.parse_args()

    main(args)
