import requests as r


base = "https://github.com"
domain = 'github.com'
remaining_pages = 20
frontier = ["https://github.com/DannyK05"]
known_href = set("https://github.com/DannyK05")

def url_parser(href: str, base: str):
    """
    (str, str) -> str | None

    Normalizes an href into an absolute URL when possible.

    Root-relative URLs are combined with the base URL.
    Absolute HTTP/HTTPS URLs are returned unchanged.
    Unsupported or unrecognized href values return None.
    """

    if href[0] == "/":
        return base + href
    elif href[0:3] == "http":
        return href
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

    # print(parser.feed(html_body))
    i = 0
    # parse the html_body to extract href values
    while(i < len(html_body)-4):
        href_char = ""
        j = i
        if (html_body[i:i+6] == 'href="'):
            j+=6
            while(j < len(html_body) and html_body[j]!= '"'):
                href_char += html_body[j]
                j+=1 
            if href_char.strip() != "":
                hrefs.add(href_char)

        i += (j-i) + 1

   #parse the href to normalize it and convert them to valid hrefs
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
 

print(frontier)
