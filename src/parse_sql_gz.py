import gzip
from collections.abc import Generator
from pathlib import Path

import pandas as pd
from tqdm import tqdm


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


if __name__ == "__main__":
    path_to_file = Path("local_data/dawiki-latest-category.sql.gz")
    sql_content = read_sql_gz(path_to_file)
    all_records = []
    for line in tqdm(sql_content):
        records = parse_sql_inserts(line)
        print(f"found {len(records) if records else 0} records")
        all_records.extend(records)
    col_names = ["cat_id", "cat_title", "cat_pages", "cat_subcats", "cat_files"]
    real_recors = [record for record in all_records if len(record) == len(col_names)]
    df = pd.DataFrame(real_recors, columns=col_names)

    df.to_csv("local_data/dawiki-latest-category.csv", index=False)

    new_path = Path("local_data/dawiki-latest-categorylinks.sql.gz")
    new_sql_content = read_sql_gz(new_path)
    all_new_records = []
    for line in tqdm(new_sql_content):
        new_records = parse_sql_inserts(line)
        all_new_records.extend(new_records)

    new_columns = [
        "cl_from",
        "cl_to",
        "cl_sortkey",
        "cl_timestamp",
        "cl_sortkey_prefix",
        "cl_collation",
        "cl_type",
    ]
    new_real_records = [
        record for record in all_new_records if len(record) == len(new_columns)
    ]

    new_df = pd.DataFrame(new_real_records, columns=new_columns)
    new_df.loc[new_df["cl_type"] == "'subcat'", ["cl_from", "cl_to"]].to_csv(
        "local_data/dawiki-latest-categorylinks.csv",
        index=False,
    )

    pagepath = Path("local_data/dawiki-latest-page.sql.gz")
    pages = []
    for line in tqdm(read_sql_gz(pagepath)):
        records = parse_sql_inserts(line)
        pages.extend(records)

    CATEGORYSPACE = "14"
    columns = ["cat_id", "cat_title"]
    cats = [(record[0], record[2]) for record in pages if record[1] == CATEGORYSPACE]
    catdf = pd.DataFrame(cats, columns=columns)
    catdf.to_csv("local_data/dawiki-category-ids.csv", index=False)
