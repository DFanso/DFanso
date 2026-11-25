"""Turns the README's titles into vector outlines (titles.json), set in JetBrains Mono
(https://github.com/JetBrains/JetBrainsMono, SIL Open Font License 1.1).
Only these words are stored, as artwork; the font file is not in this repo.
theme.title() draws them.

Needs fontTools. Run it after changing TITLES, with the variable font from the link above:
    python .github/scripts/make_titles.py "<path to JetBrainsMono[wght].ttf>"
"""
import json
import os
import sys

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

TITLES = [
    'Leo', 'Felcianas', '$',
    'cat about.md', 'ls ~/projects', 'ls ~/stack', 'git log --streak', 'top --languages', 'neofetch',
    'echo "thanks for stopping by!"', '</>', '{ }',
]
TRACKING = 0     # extra space between letters, in em (none: it's a monospace face)
WEIGHT = 800     # JetBrains Mono's weight axis runs 100-800

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'titles.json')


def outline(font, text):
    upm = font['head'].unitsPerEm
    cmap, glyphs, hmtx = font.getBestCmap(), font.getGlyphSet(), font['hmtx']
    pen = SVGPathPen(glyphs, ntos=lambda v: f'{v:.0f}')
    x = 0
    for i, ch in enumerate(text):
        name = cmap.get(ord(ch)) or cmap.get(ord(ch.upper()))
        if name is None:
            raise SystemExit(f'The font has no glyph for {ch!r} in {text!r}')
        # Font units are y-up; flip so the path drops straight into SVG with its baseline at y=0.
        glyphs[name].draw(TransformPen(pen, (1, 0, 0, -1, x, 0)))
        x += hmtx[name][0] + (TRACKING * upm if i < len(text) - 1 else 0)
    return {'d': pen.getCommands(), 'width': round(x), 'upm': upm}


def main():
    font = TTFont(sys.argv[1])
    if 'fvar' in font:
        axes = {a.axisTag for a in font['fvar'].axes}
        font = instantiateVariableFont(font, {k: v for k, v in {'wght': WEIGHT, 'wdth': 100}.items() if k in axes})
    data = {t: outline(font, t) for t in TITLES}
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, separators=(',', ':'))
    print(f'{len(data)} titles, {os.path.getsize(OUT):,} bytes')


if __name__ == '__main__':
    main()
