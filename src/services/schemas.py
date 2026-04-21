from dataclasses import dataclass


@dataclass
class RawDocumentSchema:
    filename: str
    content: str
