import requests as r

hrefs = set()

response = r.get("https://github.com/DannyK05")
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

print(list(hrefs))
# for href in list(hrefs):
#     if href[i] == '/':
