from pathlib import Path

from huggingface_hub import HfApi, login

DATA_DIR = Path("local_data")
PREFIXES = ["da", "sq", "lv", "gv"]


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
    for prefix in PREFIXES:
        upload_wiki_lang(api, prefix=prefix)


if __name__ == "__main__":
    main()
