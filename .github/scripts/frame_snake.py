"""Fits the contribution snake (from Platane/snk) into a terminal window as wide as
the README's other blocks, with a caption under it, in the theme (see theme.py).
Run by .github/workflows/profile-assets.yml after the snake is generated.

Usage: python frame_snake.py <snake.svg> <out.svg>
"""
import re
import sys

from theme import BLINK, DEPTH, GREEN, MONO, PAD, TEXT_DIM, svg, window


def main():
    src, out = sys.argv[1], sys.argv[2]
    with open(src, encoding='utf-8') as f:
        snake = f.read()
    vb = re.search(r'viewBox="([^"]+)"', snake).group(1)
    vx, vy, vw, vh = (float(v) for v in vb.split())
    inner = re.sub(r'^.*?<svg[^>]*>|</svg>\s*$', '', snake, flags=re.S)

    # snk leaves a 16px margin round the grid and room under it that the snake never uses; trim
    # both so the grid lines up with the panels' edges and the caption sits close.
    vx, vw, vh = vx + 14, vw - 28, vh - 36
    vb = f'{vx:g} {vy:g} {vw:g} {vh:g}'
    W, side, bar = 1000, 28, 40
    gw = W - 2 * side
    h = vh * gw / vw
    top = bar + 24
    wh = round(top + h + 42)
    H = wh + DEPTH + PAD
    body = f'''{window(W, wh, '~/contributions — snake', 'sn', glow=(GREEN[2], .5, 1, .6))}
<svg x="{side}" y="{top}" width="{gw}" height="{h:.0f}" viewBox="{vb}">{inner}</svg>
<text x="{side + 4}" y="{wh - 16}" font-family="{MONO}" font-size="11.5" fill="{TEXT_DIM}"># one square = one day of contributions · last 12 months</text>
<text x="{W - side - 4}" y="{wh - 16}" font-family="{MONO}" font-size="11.5" font-weight="700" fill="{GREEN[1]}" text-anchor="end">eating commits<tspan class="cursor"> ▌</tspan></text>'''
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write(svg(W, H, 'A snake eating my contribution graph', body, BLINK))


if __name__ == '__main__':
    main()
