import requests
from bs4 import BeautifulSoup, NavigableString, Tag, Comment

def extract_texts(element):
    if isinstance(element, Comment):
        return ''
    elif isinstance(element, NavigableString):
        return element.string.strip()
    elif isinstance(element, Tag):
        content = ''
        if element.name.lower() in ('span', 'p', 'table', 'tr', 'th', 'td', 'tbody', 'body', 'div', 'center', 'strong', 'em', 'i', 'b'):        
            for child in element.children:
                content += extract_texts(child)

        if element.name.lower() in ('p', 'br', 'div'):
            content += '\n'
        return content
    return ''

def convert(url):
    r = requests.get(url)
    r.raise_for_status()
    doc = BeautifulSoup(r.text, 'html.parser')
    body = doc.find('body')
    print(extract_texts(body))

if __name__ == '__main__':
    url = 'https://mailchi.mp/bajour/283-4748137'
    convert(url)
