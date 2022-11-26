from PIL import Image, ImageEnhance
import numpy as np
import requests
import io

def image_url_to_bitmap(url, width):
    r = requests.get(url)
    r.raise_for_status()
    im = Image.open(io.BytesIO(r.content))
    im = im.convert('RGBA')
    enhancer = ImageEnhance.Brightness(im)
    im = enhancer.enhance(2)
    height = int(im.height / im.width * width)
    im = im.resize((width, height))
    im = im.convert('1')
    return im
     

