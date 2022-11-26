            


def main():
    font_name = "bitmap-fonts/BaseSeven/Base Seven 14px.foni"
    font, args = PILtxt.fromfonifile(font_name)
    byte_width = 48
    width = 8*byte_width
    line_space = 2
    
    y = 0
    # text = "dasdasdasdasdddddddf ist ein test mit einem länggerem sätzli das das ist ein test mit einem länggerem sätzli das istist ein test mit einem länggerem sätzli dasdasdasdas ist ein test mit einem länggerem sätzli das das ist ein test mit einem länggerem sätzli das istist ein test mit einem länggerem sätzli dasdasdasdas ist ein test mit einem länggerem sätzli das das ist ein test mit einem länggerem sätzli das istist ein test mit einem länggerem sätzli dasdasdasdas ist ein test mit einem länggerem sätzli das das ist ein test mit einem länggerem sätzli das istist ein test mit einem länggerem sätzli dasdasdasdas ist ein test mit einem länggerem sätzli\n das das ist ein test mit einem länggerem sätzli das istist ein test mit einem länggerem sätzli"
    # text = 'a' * 50
    text = sys.argv[1]
    lines = list(break_text(text, font, width))
    im = Image.new('1', (width, font.ch * (1 + len(lines))), color=1)
    for line in lines:
        print('---> ', line)
        font.textout(im, line, 0, y)
        y += font.text_size(line)[1] + line_space
    im.show()
    arr = np.array(im, dtype='?')
    arr = np.invert(arr)
    binary = np.packbits(arr)
    # im.save('outfile.bmp')
    for i, byte in enumerate(binary):
        if i % byte_width == 0:
            print()
        print('%02x' % byte, end=" ")
        
    with open('outfile.bin', 'wb') as outfile: 
        for byte in binary:
            outfile.write(byte)
main()