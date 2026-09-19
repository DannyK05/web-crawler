import requests as r
from bs4 import BeautifulSoup
from utils.index import tokenize

query= "Who is DannyK05"
base = "https://github.com"
domain = 'github.com'
index = {}
remaining_pages = 20
frontier = ["https://github.com/DannyK05"]
known_href = {"https://github.com/DannyK05"}


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
    
    

def valid_url(url:str, domain:str):
    """
    (str, str) => bool

    Checks if a url is valid within the domain of crawler

    """
    url_sections = url.split("/")
    if url_sections[2] == domain:
        return True
    else:
        return False

tokens:list[str] = tokenize(query)
print(tokens,"tokens")


def crawl (url:str,frontier:list[str]):
    global remaining_pages
    hrefs:set[str] = set()
    response = r.get(url)
    html_body = response.text
    
    if (not response.ok):
        remaining_pages +=1
        return

    if ("html" not in response.headers["Content-Type"]):
        remaining_pages +=1
        return

  # parse the html_body to extract href values
    soup = BeautifulSoup(html_body,"html.parser")
    title = soup.title.string
    description = soup.select('meta[name="description"]')[0]['content']
    website_text = soup.get_text(" ", strip=True).lower()
  
  
    for token in tokens:
        if token in website_text:
            if token not in index:
                index[token] = [{"title": title, "preview": description,"url":url}]
            else:
                index[token].append({"title": title, "preview": description,"url":url})
            
    anchor_tags = soup.select("a[href]")
    
    for anchor in anchor_tags:
        hrefs.add(str(anchor['href']))

   # parse the href to normalize it and convert them to valid hrefs
    for href in list(hrefs):
        parsed_url = url_parser(href, base)
        if parsed_url and  valid_url(parsed_url, domain):
            if parsed_url not in known_href:
                frontier.append(parsed_url)
                known_href.add(parsed_url)
                

# Crawling loop
while (len(frontier) > 0 and remaining_pages > 0):
    print(remaining_pages)
    next_href = frontier.pop()
    crawl(next_href,frontier)
    remaining_pages -= 1
 

print(index)
# print(frontier)
