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


def tokenize(query:str):
    """
    (str) => str[]
    
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


# def stemm (tokens:list[str]):
#     result = []
#     for token in tokens:
#         if token.endswith("ed")