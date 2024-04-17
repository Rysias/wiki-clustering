from pathlib import Path

from huggingface_hub import HfApi, login

DATA_DIR = Path("local_data")
CONFIG_DIR = Path("language_configs")
PREFIXES = ["da", "sq", "lv", "gv"]


def get_prefix(file: Path) -> str:
    return file.stem.split("-")[0]


def get_all_prefixes() -> list[str]:
    return [get_prefix(conffile) for conffile in CONFIG_DIR.glob("*.json")]


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
    for prefix in get_all_prefixes():
        print(f"Uploading {prefix}")
        upload_wiki_lang(api, prefix=prefix)


if __name__ == "__main__":
    main()
