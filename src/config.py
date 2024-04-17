from dataclasses import dataclass

import src.fileio as fileio


@dataclass
class Config:
    prefix: str
    category: str
    infobox: str
    file: str
    top_level: str

    @classmethod
    def from_json(cls: "Config", file: str) -> "Config":
        config = fileio.read_json(file)
        return cls(**config)
