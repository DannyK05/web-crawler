import math


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
    cur,
    tokens: list[str],
):
    doc_ranking = {}
    rank_details = []

    cur.execute(
        """
        SELECT COUNT(*)
        FROM documents
        """
    )
    total_docs = cur.fetchone()[0]

    for token in tokens:
        cur.execute(
            """
            SELECT *
            FROM document_tokens
            WHERE token_id = (
            SELECT token_id
            FROM tokens
            WHERE token = %s
            )
            """,
            (token,),
        )

        details = cur.fetchall()

        if len(details) != 0:
            for detail in details:
                score = (detail[3] / detail[2]) * (
                    math.log10(total_docs / len(details))
                )
                if detail[1] not in doc_ranking:
                    doc_ranking[detail[1]] = score
                else:
                    doc_ranking[detail[1]] += score

    for key, value in doc_ranking.items():
        token_detail = {"document_id": key, "score": value}
        rank_details.append(token_detail)

    for i in range(len(rank_details)):
        for j in range(len(rank_details) - i - 1):
            if rank_details[j]["score"] < rank_details[j + 1]["score"]:
                buff = rank_details[j]
                rank_details[j] = rank_details[j + 1]
                rank_details[j + 1] = buff

    return rank_details


def extract_ranked_documents(cur, ranked_docs: list[dict]):
    """
    (list[dict]) => list[dict]

    Extracts the document details from the ranked documents

    """
    doc_details = []
    for doc in ranked_docs:
        cur.execute(
            """
            SELECT *
            FROM documents
            WHERE document_id = %s
            """,
            (doc["document_id"],),
        )
        details = cur.fetchone()
        doc_detail = {
            "document_id": details[0],
            "title": details[1],
            "preview": details[2],
            "url": details[3],
        }
        doc_details.append(doc_detail)

    return doc_details
