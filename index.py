import os
from collections import Counter, deque

import psycopg
import requests as r
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from crawler_types import Document
from utils.index import extract_ranked_documents, rank, tokenize, url_parser, valid_url

load_dotenv()


def crawl(cur, domain, base, url: str, frontier: deque[str], known_href: set[str]):
    hrefs: set[str] = set()
    response = r.get(url)
    html_body = response.text

    if not response.ok:
        return

    if "html" not in response.headers["Content-Type"]:
        return

    # parse the html_body to extract href values
    soup = BeautifulSoup(html_body, "html.parser")
    title = ""
    description = ""

    if soup.title and soup.title.string:
        title = soup.title.string

    if soup.select('meta[name="description"]')[0]["content"]:
        description = soup.select('meta[name="description"]')[0]["content"]

    # TODO: Add a handler for site without title tag and meta tags

    document: Document = {"title": title, "preview": str(description), "url": url}

    cur.execute(
        """
            INSERT INTO documents (title, preview, url) 
            VALUES (%s, %s, %s)
            ON CONFLICT (url) DO NOTHING
            RETURNING document_id;
            """,
        (document["title"], document["preview"], document["url"]),
    )
    if cur.rowcount > 0:
        document_id = cur.fetchone()[0]
    else:
        cur.execute(
            """
            SELECT document_id
            FROM documents
            WHERE url = %s;
            """,
            (document["url"],),
        )
        document_id = cur.fetchone()[0]

    website_text = soup.get_text(" ", strip=True).lower()
    words = tokenize(website_text)
    document_size = len(words)
    word_count = Counter(words)

    for word, count in word_count.items():
        cur.execute(
            """
                INSERT INTO tokens (token) 
                VALUES (%s)
                ON CONFLICT (token) DO NOTHING
                RETURNING token_id;
                """,
            (word,),
        )

        if cur.rowcount > 0:
            token_id = cur.fetchone()[0]
        else:
            cur.execute(
                """
                SELECT token_id
                FROM tokens
                WHERE token = %s
                """,
                (word,),
            )
            token_id = cur.fetchone()[0]

        cur.execute(
            """
                INSERT INTO document_tokens (token_id, document_id, document_size, token_count) 
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (token_id, document_id) DO NOTHING;
                """,
            (token_id, document_id, document_size, count),
        )

    anchor_tags = soup.select("a[href]")

    for anchor in anchor_tags:
        hrefs.add(str(anchor["href"]))

    # parse the href to normalize it and convert them to valid hrefs
    for href in list(hrefs):
        parsed_url = url_parser(href, base)
        if (
            parsed_url
            and (parsed_url not in known_href)
            and valid_url(parsed_url, domain)
        ):
            frontier.appendleft(parsed_url)
            known_href.add(parsed_url)


def search_engine(query):
    base = "https://github.com"
    domain = "github.com"
    remaining_pages = 100
    frontier = deque(["https://github.com/DannyK05"])
    known_href = {"https://github.com/DannyK05"}

    conn = psycopg.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

    cur = conn.cursor()
    cur.execute(
        """
            CREATE TABLE IF NOT EXISTS documents(
                document_id SERIAL PRIMARY KEY,
                title TEXT,
                preview TEXT,
                url TEXT UNIQUE
            );

            CREATE TABLE IF NOT EXISTS tokens(
                token_id SERIAL PRIMARY KEY,
                token TEXT UNIQUE
            );

            CREATE TABLE IF NOT EXISTS document_tokens(
                token_id INT REFERENCES tokens(token_id),
                document_id INT REFERENCES documents(document_id),
                document_size INT,
                token_count INT,
                PRIMARY KEY (token_id, document_id)
            );
            """
    )

    tokens: list[str] = tokenize(query)
    rank_details = rank(cur, tokens)
    if len(rank_details) >= 10:
        return extract_ranked_documents(cur, rank_details)

    # Crawling loop
    while len(frontier) > 0 and remaining_pages > 0:
        new_ranking = rank(cur,tokens)
        if len(new_ranking) > 10:
            break
        print(remaining_pages)
        next_href = frontier.pop()
        crawl(cur, domain, base, next_href, frontier, known_href)
        remaining_pages -= 1

    conn.commit()
    cur.close()
    conn.close()

    return extract_ranked_documents(cur, rank_details)


result = search_engine("JusticeEnams")

print(result)
