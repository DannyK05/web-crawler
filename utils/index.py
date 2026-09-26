import math

from crawler_types import TokenIndex


def url_parser(href: str, base: str):
    """
    (str, str) -> str | None

    Normalizes an href into an absolute URL when possible.

    Root-relative URLs are combined with the base URL.
    Absolute HTTP/HTTPS URLs are returned unchanged.
    Unsupported or unrecognized href values return None.
    """

    if len(href) == 0:
        return None
    elif href[0] == "/":
        return base + href
    elif href[0:3] == "http":
        return href
    else:
        return None


def valid_url(url: str, domain: str):
    """
    (str, str) => bool

    Checks if a url is valid within the domain of crawler

    """
    url_sections = url.split("/")
    return url_sections[2] == domain


def tokenize(query: str):
    """
    (str) => list[str]

    Returns processed tokens from a string;

    """
    tokens = query.split(" ")
    processed_tokens = []
    for token in tokens:
        stripped_token = token.strip()
        if stripped_token == "":
            continue
        processed_tokens.append(stripped_token.lower())

    return processed_tokens


def rank(
    token_index:TokenIndex , tokens: list[str], total_docs: int
):
    doc_ranking = {}
    rank_details = []

    for token in tokens:
        if token in token_index:
            for detail in token_index[token]:
                rank = (detail["word_count"] / detail["document_size"]) * (
                    math.log10(total_docs / len(token_index[token]))
                )
                if detail["document_id"] not in doc_ranking:
                    doc_ranking[ detail["document_id"]] = rank
                else:
                     doc_ranking[ detail["document_id"]] += rank

    for key,value in doc_ranking.items():
        token_detail = {"document_id": key, "rank": value}
        rank_details.append(token_detail)

    for i in range(len(rank_details)):
        for j in range(i, len(rank_details) - i - 1):
            if rank_details[j]["rank"] < rank_details[j + 1]["rank"]:
                buff = rank_details[j]
                rank_details[j] = rank_details[j + 1]
                rank_details[j + 1] = buff
    return rank_details


# def stemm (tokens:list[str]):
#     result = []
#     for token in tokens:
#         if token.endswith("ed")
