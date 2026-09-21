import requests as r
from bs4 import BeautifulSoup
from utils.index import tokenize, url_parser, valid_url

query= "Who is DannyK05"
base = "https://github.com"
domain = 'github.com'
token_index = {}
document_index = {}
remaining_pages = 20
frontier = ["https://github.com/DannyK05"]
known_href = {"https://github.com/DannyK05"}



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
    document_id = 1

    if len(document_index) > 0:
         document_id = next(reversed(document_index)) + 1 #increments the last id used in the dict
# todo: check if document exists before adding to the document index

    document_index[document_id] = {"title": title, "preview": description,"url":url}

    website_text = soup.get_text(" ", strip=True).lower()
  
  
    for word in tokenize(website_text):
        if word in token_index:
            token_index[word].append(document_id)
        else:
            token_index[word] = [document_id]
            
            
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
 

# Result generation
result = {}
for token in tokens:
    result[token] = []
    if token in token_index:
        for index in token_index[token]:
            result[token].append(document_index[index])

    

print(token_index)
print("\n------------------------------------------------------------------------\n")
print(document_index)
print("\n------------------------------------------------------------------------\n")
print(result)
print("\n------------------------------------------------------------------------\n")
print(token_index['kolade'])
print("\n------------------------------------------------------------------------\n")
print(token_index['dannyk05'])

# print(frontier)
