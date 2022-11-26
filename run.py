import json
from webtobitmap.download import convert
import numpy as np
import requests

def main():
    r = requests.get('https://bajour.ch/api/latest-mailchimp-campaign-no-date')
    r.raise_for_status()
    result = r.json()
    url = result['longArchiveURL']
    with open('outfile.bin', 'wb') as outfile:
        for i, img in enumerate(convert(url)):
            arr = np.array(img, dtype='?')
            arr = np.invert(arr)
            # img.save(f"{i}.bmp")
            for byte in np.packbits(arr):
                outfile.write(byte)

main()