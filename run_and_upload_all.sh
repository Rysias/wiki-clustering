#!/bin/bash

# Download all the files
poetry run python src/download_wikidump.py

# Loop over all the config files in language_configs/
for config_file in language_configs/*; do
    # Print a message indicating which config file is being processed
    echo "Processing $config_file"
    
    # Run run_for_lang.sh for each config file
    ./run_for_lang.sh "$config_file"
done

echo "Creating categories"
poetry run python src/create_categories.py

echo "Uploading to Hugging Face"
poetry run python src/upload_hf.py