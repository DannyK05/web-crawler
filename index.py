import requests as r

base = "https://github.com"
domain = 'github.com'
page_count = 20
normalized_href = ["https://github.com/DannyK05"]
known_href = set()

def url_parser(url:str, base:str):
    if url[0] == "/":
        return base + url
    elif url[0:3] == "http":
        return url
    return None
    
    

def valid_url(url:str, domain:str):
    url_sections = url.split("/")
    # print(url_sections)
    if url_sections[2] == domain:
        return True
    else:
        return False


def crawl (url:str,normalized_href:list[str]):
    hrefs:set[str] = set()

    response = r.get(url)
    html_body = response.text

    i = 0
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

    # print(list(hrefs))


    for href in list(hrefs):
        parsed_url = url_parser(href, base)
        if parsed_url and  valid_url(parsed_url, domain):
            if parsed_url not in known_href:
                normalized_href.append(parsed_url)
                known_href.add(parsed_url)
                


while (len(normalized_href) > 0 and page_count > 0):
    print(page_count)
    next_href = normalized_href.pop()
    crawl(next_href,normalized_href)
    page_count -= 1

    

print(normalized_href)
