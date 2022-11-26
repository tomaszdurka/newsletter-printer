import requests
from bs4 import BeautifulSoup, NavigableString, Tag, Comment
import re
from .text import text_to_bitmap
from .image import image_url_to_bitmap

class ImageReference:
    def __init__(self, url):
        self.url = url

def extract_elements(element):
    if isinstance(element, Comment):
        pass
    elif isinstance(element, NavigableString):
        yield element.string.replace('\n', ' ').replace('\r', ' ').strip()
    elif isinstance(element, Tag):
        content = ''
        if element.name.lower() == 'img':
            print("image", element['src'])
            yield ImageReference(element['src'])
            return
        elif element.name.lower() in ('span', 'p', 'table', 'tr', 'th', 'td', 'tbody', 'body', 'div', 'center', 'strong', 'em', 'i', 'b'):        
            for child in element.children:
                child_elements = extract_elements(child)
                for child_content in child_elements:
                    yield child_content

        if element.name.lower() in ('p', 'br', 'div'):
            yield '\n'
        

def reduce_elements(elements):
    text = ''
    for item in elements:
        if isinstance(item, str):
            item = item.strip(' ')
            text += ' ' + item
        else:
            yield text
            yield item
            text = ''
    yield text
        

def convert(url):
    r = requests.get(url)
    r.raise_for_status()
    doc = BeautifulSoup(r.text, 'html.parser')
    body = doc.find('body')
    width = 384
    for i, item in enumerate(reduce_elements(extract_elements(body))):
        if isinstance(item, str):
            item = re.sub(r"[ ]+", ' ', item)
            item = re.sub(r"\n\s+", '\n', item, re.MULTILINE)
            item = re.sub(r"\s+\n", '\n', item, re.MULTILINE)
            yield text_to_bitmap(item, width)
        elif isinstance(item, ImageReference):
            yield image_url_to_bitmap(item.url, width)

