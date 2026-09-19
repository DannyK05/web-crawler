
def tokenize(query:str):
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