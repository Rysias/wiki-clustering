# wiki-clustering
Code for creating clustering benchmarks for arbitrary languages using wikipedia. 

## Installation
The project uses `poetry` for dependency management - make sure you have it install (see [this guide for](https://python-poetry.org/docs/#installation) for instructions). To install the dependencies, run:
```bash
poetry install
```

## Usage
### Config files
Adding a new language has two steps; a) downloading the right files from the wikipedia dump and b) writing a configuration file called `{prefix}-config.json` and storing it in [`language_configs/`](./language_configs/). The structure of the config file can be found in [`src/config.py`](./src/config.py).

### Scripts
There are a bunch of scripts to run the different parts of the pipeline. The main ones are:

- [`parse_articles.py`](./src/parse_articles.py): Parses the articles to create a json with the first paragraphs and the categories for the first 300,000 articles of the wiki dump. 
- [`parse_sql_gz.py`](./src/parse_sql_gz.py): Parses the SQL dump of the wikipedia to get the categories of the articles as well as their ids. This includes the top-levle  
- [`join_categories.py`](./src/join_categories.py): Joins the categories from the SQL dump with the articles from the parsed articles. Specifically, this joins the categories with the top-level categories as defined from the corresponding language article to [Main topic classifications](https://en.wikipedia.org/wiki/Category:Main_topic_classifications). 
- [`create_categories.py`](./src/create_categories.py): Creates the actual dataset by sampling from the articles and the corresponding categories. 
- [`upload_hf.py`](./src/upload_hf.py): Uploads the dataset to Hugging Face. NB: Currently this can only be done by the author (me!).

### Running the pipeline
For convenience, there are two helper scripts for running the pipeline: [`run_for_lang.sh`](./run_for_lang.sh) and [`run_all.sh`](./run_all.sh). The former runs the pipeline for a single language, while the latter runs the pipeline for all languages in the `language_configs/` directory.


## TODO: 
- [x] Create a read-like file on HF a la [this one](https://huggingface.co/datasets/mteb/amazon_reviews_multi/blob/main/amazon_reviews_multi.py)
- [x] Simple documentation on how the data was created.

## Languages
### Signs
- x: all done
- c: config file written
- r: download and run
- e: evaluated
- h: uploaded and update hf

### Languages
- [x] da
- [x] lv
- [x] gv
- [x] sq
- [ ] ku
- [ ] sco
- [ ] mt
- [ ] bs
- [ ] ca
- [ ] eu
- [ ] wa
- [ ] cs
- [ ] ilo
- [ ] min