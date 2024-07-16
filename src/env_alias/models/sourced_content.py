from dataclasses import dataclass


@dataclass
class SourcedContent:
    source: str
    source_method: str
    content: str
    content_type: str

    def __post_init__(self) -> None:
        self.content_type = self.content_type.lower()
        self.source_method = self.source_method.lower()
