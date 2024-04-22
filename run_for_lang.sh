#!/bin/bash

# Check if a configuration path was provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <config-path>"
    exit 1
fi

config_path="$1"

# Run each Python script using Poetry, with the config path as an argument
poetry run python src/parse_articles.py --config-path "$config_path" --num-articles 300000
poetry run python src/parse_sql_gz.py --config-path "$config_path"
poetry run python src/join_categories.py --config-path "$config_path"
