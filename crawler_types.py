from typing import TypedDict


class TokenDetails(TypedDict):
    document_id: int
    document_size: int
    word_count: int

TokenIndex = dict[str, list[TokenDetails]]


class Document(TypedDict):
    title: str
    preview: str
    url: str

DocumentIndex = dict[int, Document]

