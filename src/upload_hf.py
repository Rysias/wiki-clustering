from pathlib import Path

from huggingface_hub import HfApi, login

import src.fileio as fileio

DATA_DIR = Path("local_data")


def upload_wiki_lang(
    api: HfApi,
    prefix: str,
    repo_name: str = "ryzzlestrizzle/multi-wiki-clustering-p2p",
):
    api.upload_file(
        path_or_fileobj=DATA_DIR / prefix / "test.jsonl.gz",
        path_in_repo=f"{prefix}/test.jsonl.gz",
        repo_id=repo_name,
        repo_type="dataset",
    )


def main():
    login()
    api = HfApi()
    for prefix in fileio.get_all_prefixes():
        print(f"Uploading {prefix}")
        upload_wiki_lang(api, prefix=prefix)


if __name__ == "__main__":
    main()
