from collections import Counter

import requests as r
from bs4 import BeautifulSoup

from utils.index import rank, tokenize, url_parser, valid_url

query = "Who is DannyK05"
base = "https://github.com"
domain = "github.com"
token_index = {}
document_index = {}
remaining_pages = 20
frontier = ["https://github.com/DannyK05"]
known_href = {"https://github.com/DannyK05"}


tokens: list[str] = tokenize(query)
print(tokens, "tokens")


def crawl(url: str, frontier: list[str]):
    global remaining_pages
    hrefs: set[str] = set()
    response = r.get(url)
    html_body = response.text

    if not response.ok:
        remaining_pages += 1
        return

    if "html" not in response.headers["Content-Type"]:
        remaining_pages += 1
        return

    # parse the html_body to extract href values
    soup = BeautifulSoup(html_body, "html.parser")
    title = soup.title.string
    description = soup.select('meta[name="description"]')[0]["content"]
    document_id = 1

    if len(document_index) > 0:
        document_id = (
            next(reversed(document_index)) + 1
        )  
    # increments the last id used in the dict
    # todo: check if document exists before adding to the document index

    document_index[document_id] = {"title": title, "preview": description, "url": url}

    website_text = soup.get_text(" ", strip=True).lower()
    words = tokenize(website_text)
    document_size = len(words)
    word_count = Counter(words)

    for word in words:
        token_details = {
            "document_id": document_id,
            "document_size": document_size,
            "word_count": word_count[word],
        }
        if word in token_index:
            if token_details not in token_index[word]:
                token_index[word].append(token_details)
        else:
            token_index[word] = [token_details]

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
            frontier.append(parsed_url)
            known_href.add(parsed_url)


# Crawling loop
while len(frontier) > 0 and remaining_pages > 0:
    print(remaining_pages)
    next_href = frontier.pop()
    crawl(next_href, frontier)
    remaining_pages -= 1


# Result generation
# result = {}
# for token in tokens:
#     result[token] = []
#     if token in token_index:
#         for index in token_index[token]:
#             result[token].append(document_index[index])


print(token_index)
print("\n------------------------------------------------------------------------\n")
print(document_index)
print(len(document_index))
print("\n------------------------------------------------------------------------\n")
result = rank(token_index,tokens, total_docs=len(document_index))
print(result)
# print("\n------------------------------------------------------------------------\n")
# print(token_index["dannyk05"])

# print(frontier)
