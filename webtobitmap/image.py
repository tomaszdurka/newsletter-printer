from PIL import Image, ImageEnhance
import numpy as np
import requests
import io

def image_url_to_bitmap(image_reference, width):
    url = image_reference.url
    r = requests.get(url)
    r.raise_for_status()
    im = Image.open(io.BytesIO(r.content))
    im = im.convert('RGBA')
    enhancer = ImageEnhance.Brightness(im)
    im = enhancer.enhance(2)
    print(image_reference.size)
    if image_reference.size and image_reference.size[0] < width:
        im = im.resize((image_reference.size))

    if im.width > width:    
        height = int(im.height / im.width * width)
        im = im.resize((width, height))
    else:
        new_image = Image.new('RGBA', (width, im.height), (255, 255, 255, 0))
        new_image.paste(im, (0, 0, im.width, im.height))
        im = new_image
    im = im.convert('1')
    return im
     

