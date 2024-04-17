import gzip
import json
from collections.abc import Generator

import datasets

_LANGUAGES = {
    "da": "Danish",
    "lv": "Latvian",
    "sq": "Albanian",
    "gv": "Manx",
}
_ALL_LANGUAGES = "all_languages"
_DOWNLOAD_URL = "{lang}/{split}.jsonl.gz"
_VERSION = "1.0.0"
_DESCRIPTION = """
A dataset of wikipedia paragraphs and corresponding top-level categories for multilingual clustering.
"""


class WikiClusteringP2PConfig(datasets.BuilderConfig):
    """BuilderConfig for AmazonReviewsMultiConfig."""

    def __init__(self, languages: dict[str, str] | None = None, **kwargs):  # noqa: ANN003
        super().__init__(version=datasets.Version(_VERSION, ""), **kwargs)
        self.languages = languages


class WikiClusteringP2P(datasets.GeneratorBasedBuilder):

    """Wikipedia Clustering"""

    BUILDER_CONFIGS = [
        WikiClusteringP2PConfig(
            name=_ALL_LANGUAGES,
            languages=_LANGUAGES,
            description="A collection of wikipedia paragraphs and category labels to aid in multilingual clustering evaluation.",
        ),
    ] + [
        WikiClusteringP2PConfig(
            name=lang,
            languages=[lang],
            description=f"{_LANGUAGES[lang]} articles/labels for wikipedia articles",
        )
        for lang in _LANGUAGES
    ]
    BUILDER_CONFIG_CLASS = WikiClusteringP2PConfig
    DEFAULT_CONFIG_NAME = _ALL_LANGUAGES

    def _info(self) -> datasets.DatasetInfo:
        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            supervised_keys=None,
        )

    def _split_generators(
        self,
        dl_manager: datasets.DownloadManager,
    ) -> list[datasets.SplitGenerator]:
        test_urls = [
            _DOWNLOAD_URL.format(split="test", lang=lang)
            for lang in self.config.languages
        ]

        test_paths = dl_manager.download_and_extract(test_urls)

        return [
            datasets.SplitGenerator(
                name=datasets.Split.TRAIN,
                gen_kwargs={"file_paths": []},
            ),
            datasets.SplitGenerator(
                name=datasets.Split.VALIDATION,
                gen_kwargs={"file_paths": []},
            ),
            datasets.SplitGenerator(
                name=datasets.Split.TEST,
                gen_kwargs={"file_paths": test_paths},
            ),
        ]

    def _generate_examples(self, file_paths: list[str]) -> Generator[tuple[int, dict]]:
        row_count = 0
        for file_path in file_paths:
            with gzip.open(file_path, "rt", encoding="utf-8") as f:
                for line in f:
                    yield row_count, json.loads(line)
                    row_count += 1
