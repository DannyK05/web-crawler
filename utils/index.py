import math
import os

import psycopg
from dotenv import load_dotenv

load_dotenv()

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
    tokens: list[str],
):
    conn = psycopg.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )
    cur = conn.cursor()

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
        print(details)

     
        if len(details) != 0:
            for detail in details:
                score = (detail[3] / detail[2]) * (
                    math.log10(total_docs / len(details))
                )
                if detail[1] not in doc_ranking:
                    doc_ranking[detail[1]] = score
                else:
                    doc_ranking[detail[1]] += score
    cur.close()
    conn.close()
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


# def stemm (tokens:list[str]):
#     result = []
#     for token in tokens:
#         if token.endswith("ed")

result = rank(["who", "is", "dannyk05"])

print(result)