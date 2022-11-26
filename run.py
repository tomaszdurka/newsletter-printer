from webtobitmap.download import convert
import numpy as np
def main():
    url = 'https://mailchi.mp/bajour/283-4748137'
    with open('outfile.bin', 'wb') as outfile:
        for i, img in enumerate(convert(url)):
            arr = np.array(img, dtype='?')
            arr = np.invert(arr)
            img.save(f"{i}.bmp")
            for byte in np.packbits(arr):
                outfile.write(byte)

main()