from pydantic import BaseModel, field_validator

from .constants import ContentType, SourceMethod


class SourcedContent(BaseModel):
    """Raw content fetched from a source, with metadata about how it was obtained."""

    model_config = {"extra": "forbid"}

    source: str
    source_method: SourceMethod
    content: str
    content_type: ContentType

    @field_validator("content_type", "source_method", mode="before")
    @classmethod
    def coerce_enum(cls, v: object) -> object:
        if isinstance(v, str) and not isinstance(v, (SourceMethod, ContentType)):
            return v.lower()
        return v
