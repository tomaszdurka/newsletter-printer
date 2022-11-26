#!/usr/bin/env python

import os
from PIL import Image
import numpy as np
import bisect
from typing import Iterable, Tuple
import sys
from functools import reduce
flat_map = lambda f, xs: reduce(lambda a, b: a + b, map(f, xs))

def vwfscan_line(pxa, y, width, maxwidth, sepColor):
    """Scan along a scanline for runs of pixels other than the separator color."""
    slices = []
    for x in range(width):
        is_active = slices and slices[-1][1] is None
        is_opaque = pxa[x, y] != sepColor
        is_ending = is_active and (not is_opaque
                                   or slices[-1][0] + maxwidth <= x)
        is_starting = is_opaque and (is_ending or not is_active)
        if is_ending:
            slices[-1] = (slices[-1][0], y, x)
        if is_starting:
            slices.append((x, None))
    # If last pixel on the line was not a separator
    if slices and slices[-1][1] is None:
        slices[-1] = (slices[-1][0], y, width)
    return slices

class PILtxt(object):
    def __init__(self, im, glyphWidth, glyphHeight, maxWidth,
                 ranges=0):
        """Load a font.

im - a PIL image
glyphWidth - width of cell in which each glyph is left-aligned,
or None for proportional
glyphHeight - height of a row of glyphs
maxWidth - maximum width of a proportional glyph
ranges -- an iterable of (first CP, last CP + 1, first glyph index)
or an integer first CP (if glyphs correspond to contiguous CPs)

"""
        self.img = im
        self.cw = glyphWidth
        self.ch = glyphHeight
        if glyphWidth is None:  # Proportional font
            if len(im.mode) == 1:
                (xparentColor, sepColor) = im.getextrema()
            else:
                sepColor = (255, 0, 255)
            vwf_table = []
            pxa = im.load()
            w, h = im.size
            for yt in range(0, h, glyphHeight):
                vwf_table.extend(vwfscan_line(pxa, yt, w, maxWidth, sepColor))
        else:  # Monospace font
            vwf_table = None
        self.vwf_table = vwf_table

        # Translate first code point to code point range
        try:
            iter(ranges)
        except TypeError:
            self.ranges = [(ranges, ranges + self.num_glyphs(), 0)]
        else:
            self.ranges = sorted(ranges)

    def num_glyphs(self):
        """Count glyphs in the bitmap."""
        if self.vwf_table:
            return len(self.vwf_table)
        num_cols = (self.img.size[0] // self.cw)
        num_rows = (self.img.size[1] // self.ch)
        return num_rows * num_cols

    def codepoint_range(self):
        return (min(row[0] for row in self.ranges),
                max(row[1] for row in self.ranges))

    def cp_to_glyph(self, cp):
        try:
            cp = ord(cp)
        except TypeError:
            pass
        idx = bisect.bisect(self.ranges, (cp, cp))
        if idx > 0 and (idx >= len(self.ranges) or self.ranges[idx][0] > cp):
            idx -= 1
        l, h, run_base_cp = self.ranges[idx]
        if l <= cp < h:
            return (cp - l) + run_base_cp
        return None

    def __contains__(self, cp):
        """'r' in self: Return whether the code point has a glyph."""
        return self.cp_to_glyph(cp) is not None

    def text_size(self, txt) -> (int, int):
        txt1 = [self.cp_to_glyph(c) or 0 for c in txt]
        if not txt1:
            w = 0
        elif self.vwf_table:
            if max(txt1) >= len(self.vwf_table):
                raise IndexError(
                    "glyphid %d >= vwf_table length %d; malformed foni?"
                    % (max(txt1), len(self.vwf_table))
                )
            w = 0
            for c in txt1:
                l, _, r = self.vwf_table[c]
                w += r - l
        else:  # fixed width
            w = sum(self.cw for c in txt1)
        return (w, self.ch)

    def textout(self, dstSurface, txt, x, y):
        txt1 = [self.cp_to_glyph(c) or 0 for c in txt]
        startx = x
        wids = self.vwf_table
        if not wids:
            rowsz = self.img.size[0] // self.cw
        for c in txt1:
            if wids:
                (l, t, r) = wids[c]
            else:
                t = c // rowsz * self.ch
                if t >= self.img.size[1]:
                    continue
                l = c % rowsz * self.cw
                r = l + self.cw
            srcarea = self.img.crop((l, t, r, t + self.ch))
            dstSurface.paste(srcarea, (x, y))
            x += r - l
        return (startx, y, x, y + self.ch)

    @staticmethod
    def parse_chars(ranges):
        ranges = [r.strip().split('-', 1)
                  for line in ranges
                  for r in line.split(',')]
        rangetoglyphid = []
        glyphidbase = 0
        for line in ranges:
            firstcp = int(line[0], 16)
            lastcp = int(line[-1], 16) + 1
            rangetoglyphid.append((firstcp, lastcp, glyphidbase))
            glyphidbase += lastcp - firstcp
        rangetoglyphid.sort()
        return rangetoglyphid

    @staticmethod
    def fromfonifile(filename):
        with open(filename, 'r') as infp:
            lines = [line.strip().split('=', 1)
                     for line in infp]
        lines = [[line[0].rstrip(), line[1].lstrip()]
                 for line in lines
                 if len(line) == 2 and not line[0].startswith('#')]
        args = dict(lines)
        args['chars'] = [line[1] for line in lines if line[0] == 'chars']
        ranges = PILtxt.parse_chars(args['chars'])
        imname = os.path.join(os.path.dirname(filename), args['image'])
        im = Image.open(imname)
        height = int(args['height'])
        try:
            width = int(args['width'])
        except KeyError:
            width = None
        if not ranges:
            try:
                ranges = int(args['firstcp'], 0)
            except KeyError:
                ranges = 32
        try:
            maxwidth = int(args['maxwidth'], 0)
        except KeyError:
            maxwidth = im.size[0]
        return PILtxt(im, width, height, maxwidth, ranges), args

def break_words(words):
    for word in words:
        if '-' in word:
            parts = word.split('-')
            for part in parts[:-1]:
                yield part + '-'
            yield parts[-1]
        else:
            yield word

replace_map = {
    '⭐': '*',
}

def break_text(text: str, font: PILtxt, max_width = 200) -> Iterable[str]:
    for line in text.splitlines():
        index_search_start = 0
        line = line.strip()
        words = list(break_words(map(lambda word: word + ' ', filter(bool, line.split(' ')))))
        if not words:
            yield ''
            continue
        words_in_output_line = [words.pop(0)]
        while words:
            while words and font.text_size(''.join(words_in_output_line))[0] < max_width:
                words_in_output_line.append(words.pop(0))
            
            # if words:
            if len(words_in_output_line) == 1:
                yield words_in_output_line[0]
                if words:
                    words_in_output_line = [words.pop(0)]
            else:
                yield ''.join(words_in_output_line[:-1])
                words_in_output_line = words_in_output_line[-1:]
        yield ''.join(words_in_output_line)


def text_to_bitmap(text, width):
    font_name = "bitmap-fonts/BaseSeven/Base Seven 14px.foni"
    font, args = PILtxt.fromfonifile(font_name)

    line_space = 2
    
    y = 0
    lines = list(break_text(text, font, width))
    if lines:
        height = (font.ch * len(lines)) + ((len(lines) - 1)* line_space)
    else:
        height = 2
    print ((width, height), lines)
    im = Image.new('1', (width, height), color=1)
    for line in lines:
        print('---> ', line)
        font.textout(im, line, 0, y)
        y += font.text_size(line)[1] + line_space
    return im
    
    
    # im.save('outfile.bmp')
    # for i, byte in enumerate(binary):
    #     if i % byte_width == 0:
    #         print()
    #     print('%02x' % byte, end=" ")
        
    # with open('outfile.bin', 'wb') as outfile: 
    #     for byte in binary:
    #         outfile.write(byte)