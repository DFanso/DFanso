"""Shared look for the profile README's artwork (draw_assets.py) and live
stat cards (stat_cards.py): a dark editor / terminal theme with real depth.
Every block is a window that stands off the page (an extruded lip, a soft
shadow, a title bar with the three dots), set in a monospace face, with
isometric 3D for the illustrations. Plain SVG with CSS animation.

Everything is inlined (logos and title outlines included) because GitHub shows
these files as images, and an SVG loaded as an image can't fetch anything.
"""
import base64
import math
import os
import re
from html import escape as esc

HERE = os.path.dirname(os.path.abspath(__file__))
ICONS = os.path.join(HERE, 'icons')

MONO = "'JetBrains Mono', ui-monospace, 'SF Mono', 'Cascadia Mono', 'Fira Code', Consolas, 'Liberation Mono', monospace"
# Kept for callers that want a proportional face; the theme itself is monospace throughout.
SANS = MONO

# Editor surfaces (a muted Tokyo Night). Every block carries its own background, so it reads the
# same on GitHub's light and dark pages.
NIGHT = '#16161e'       # deepest background
PANEL = '#1a1b26'       # window body
PANEL_TOP = '#1f2133'
BAR = '#24283b'         # title bars
EDGE = '#2f354d'        # window outline
CARD = '#1f2335'        # raised cards inside a window
CARD_TOP = '#292e42'
LIP = '#0b0c12'         # the dark extrusion under a window or card
SLOT = '#14151f'        # sunken wells (bars, slots)

TEXT = '#c8d3f5'
TEXT_SOFT = '#a9b1d6'
TEXT_DIM = '#737aa2'

# Accents: (light face, main, dark face), so they can be used on 3D boxes too.
GREEN = ('#c3e88d', '#9ece6a', '#6f9b45')
CYAN = ('#b4f9f8', '#7dcfff', '#4f9fcf')
BLUE = ('#b4c8ff', '#7aa2f7', '#5072c2')
PURPLE = ('#dcc6ff', '#bb9af7', '#8f6fcf')
AMBER = ('#ffdca8', '#e0af68', '#b0843f')
RED = ('#ffb3c0', '#f7768e', '#c4506a')
STEEL = ('#4a5272', '#3a405c', '#2d3249')        # isometric hardware
STEEL_LIGHT = ('#5d6688', '#4a5272', '#3d4462')

C30, S30 = math.cos(math.pi / 6), 0.5

# Every block leaves this much clear space under itself for its shadow, so the gaps
# between blocks in the README come out the same everywhere.
PAD = 14

# The README shows every block at this share of its width (the four link tiles at a quarter of it
# each), so the blocks span exactly the dividers' line; the dividers stay at full width.
NARROW = 0.88

# How far a window stands off the page.
DEPTH = 8

REDUCED = '@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation: none !important; } }'


def svg(w, h, label, body, style=''):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{esc(label)}">\n<title>{esc(label)}</title>\n'
        f'<style>{style}\n{REDUCED}</style>\n{body}\n</svg>\n'
    )


def shadow_filter(fid, dy=10, blur=12, opacity=0.5, color='#05060a'):
    return (
        f'<filter id="{fid}" x="-30%" y="-30%" width="160%" height="180%">'
        f'<feDropShadow dx="0" dy="{dy}" stdDeviation="{blur}" flood-color="{color}" flood-opacity="{opacity}"/></filter>'
    )


def dots(x, y, r=5.5, gap=18):
    """The three window buttons."""
    return ''.join(f'<circle cx="{x + i * gap}" cy="{y}" r="{r}" fill="{c}"/>' for i, c in enumerate(('#f7768e', '#e0af68', '#9ece6a')))


def window(w, h, title='', uid='w', bar=40, x=0, y=0, rx=16, glow=None, depth=DEPTH):
    """A terminal or editor window that stands off the page: an extruded lip under it, a title bar
    with the three dots and a centred title, a faint grid on the body. The window's own height is h
    (lip excluded), so leave depth + PAD below it."""
    g = ''
    if glow:
        color, cx, cy, r = glow
        g = (f'<radialGradient id="{uid}glow" cx="{cx}" cy="{cy}" r="{r}"><stop offset="0" stop-color="{color}" stop-opacity=".16"/>'
             f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>')
    return (
        f'<defs><filter id="{uid}sh" x="-5%" y="-5%" width="110%" height="130%"><feDropShadow dx="0" dy="{depth + 4}" stdDeviation="7" '
        f'flood-color="#05060a" flood-opacity=".4"/></filter>'
        f'<linearGradient id="{uid}bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{PANEL_TOP}"/><stop offset="1" stop-color="{PANEL}"/></linearGradient>{g}'
        f'<pattern id="{uid}grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0 H0 V24" fill="none" stroke="#fff" stroke-opacity=".025"/></pattern>'
        f'<clipPath id="{uid}clip"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/></clipPath></defs>'
        f'<g filter="url(#{uid}sh)"><rect x="{x}" y="{y + depth}" width="{w}" height="{h}" rx="{rx}" fill="{LIP}"/>'
        f'<rect x="{x}" y="{y + depth * .5}" width="{w}" height="{h}" rx="{rx}" fill="#11121a"/></g>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="url(#{uid}bg)"/>'
        f'<g clip-path="url(#{uid}clip)"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{uid}grid)"/>'
        + (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{uid}glow)"/>' if glow else '')
        + (f'<rect x="{x}" y="{y}" width="{w}" height="{bar}" fill="{BAR}"/><path d="M{x} {y + bar} H{x + w}" stroke="{EDGE}" stroke-width="1.5"/>'
           f'{dots(x + 22, y + bar / 2)}'
           + (f'<text x="{x + w / 2}" y="{y + bar / 2 + 4.5}" font-family="{MONO}" font-size="12.5" font-weight="600" fill="{TEXT_DIM}" text-anchor="middle">{esc(title)}</text>' if title else '')
           if bar else '')
        + f'</g><rect x="{x + .75}" y="{y + .75}" width="{w - 1.5}" height="{h - 1.5}" rx="{rx - .75}" fill="none" stroke="{EDGE}" stroke-width="1.5"/>'
        f'<path d="M{x + rx} {y + 1.5} H{x + w - rx}" stroke="#fff" stroke-opacity=".07" stroke-width="1.5" stroke-linecap="round"/>'
    )


def raised(x, y, w, h, rx=14, top=CARD, lip=LIP, depth=6, rim=CARD_TOP):
    """A card that sits up off its window: a dark lip below, a lighter rim along the edge."""
    return (f'<rect x="{x}" y="{y + depth}" width="{w}" height="{h}" rx="{rx}" fill="{lip}"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{top}"/>'
            f'<rect x="{x + .75}" y="{y + .75}" width="{w - 1.5}" height="{h - 1.5}" rx="{rx - .75}" fill="none" stroke="{rim}" stroke-width="1.5"/>')


def badge(text, color, x, y, anchor='start', size=11.5):
    """A small bracketed status tag, like [author] or [ok]. Returns (svg, width)."""
    w = round(20 + len(text) * size * .6)
    x0 = x - w / 2 if anchor == 'middle' else x
    return (f'<g transform="translate({x0:.1f} {y})"><rect width="{w}" height="22" rx="6" fill="{color[2]}" fill-opacity=".18" '
            f'stroke="{color[1]}" stroke-opacity=".55" stroke-width="1.2"/>'
            f'<text x="{w / 2:.1f}" y="15" font-family="{MONO}" font-size="{size}" font-weight="700" fill="{color[0]}" text-anchor="middle">{esc(text)}</text></g>'), w


_TITLES = None


def title(text, x, y, size, fill=TEXT, anchor='start', extra=''):
    """A heading set in JetBrains Mono, drawn from the outlines in titles.json (made by
    make_titles.py), so no font has to load. y is the baseline. Falls back to plain text for a
    heading that hasn't been outlined yet."""
    global _TITLES
    if _TITLES is None:
        import json
        with open(os.path.join(HERE, 'titles.json'), encoding='utf-8') as f:
            _TITLES = json.load(f)
    t = _TITLES.get(text)
    if t is None:
        return (f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" font-weight="800" fill="{fill}" '
                f'text-anchor="{anchor}"{extra}>{esc(text)}</text>')
    k = size / t['upm']
    w = t['width'] * k
    x0 = x - (w / 2 if anchor == 'middle' else w if anchor == 'end' else 0)
    extra = re.sub(r'stroke-width="([\d.]+)"', lambda m: f'stroke-width="{float(m.group(1)) / k:.0f}"', extra)
    return f'<path transform="translate({x0:.1f} {y}) scale({k:.4f})" fill="{fill}"{extra} d="{t["d"]}"/>'


def title_width(text, size):
    """How wide title() draws `text` at `size` (an estimate for plain-text fallbacks)."""
    global _TITLES
    if _TITLES is None:
        title('', 0, 0, 1)
    t = _TITLES.get(text)
    return t['width'] * size / t['upm'] if t else len(text) * size * .6


def command(cmd, cx, y, size=26, color=GREEN, outline=None):
    """A section heading as a shell command, centred on cx: a green "$ " prompt, then the command.
    `outline` draws a dark stroke under it so it also reads where no window sits behind it."""
    extra = f' stroke="{outline}" stroke-width="6" stroke-linejoin="round" paint-order="stroke"' if outline else ''
    pw = title_width('$', size) + size * .6
    w = pw + title_width(cmd, size)
    x0 = cx - w / 2
    return (title('$', x0, y, size, color[1], extra=extra) + title(cmd, x0 + pw, y, size, TEXT, extra=extra)
            )


def plate(cmd, cx, y=0, size=24, color=GREEN):
    """A section heading for blocks with no window behind them: the command on its own small raised
    terminal strip, so it stays readable on GitHub's light page. Returns (svg, height)."""
    pw = title_width('$', size) + size * .6
    w = round(pw + title_width(cmd, size) + 72)
    h = 52
    x0 = cx - w / 2
    return (f'<g>{raised(x0, y, w, h, 12, PANEL_TOP, LIP, 6, EDGE)}'
            f'{command(cmd, cx, y + 35, size, color)}</g>'), h


def chip_label(text, color, x, y):
    """A small solid label (a dot and a word) that reads on any background. Returns (svg, width)."""
    w = round(32 + len(text) * 7.1)
    return (f'<g transform="translate({x} {y})"><rect y="3" width="{w}" height="26" rx="7" fill="{LIP}"/>'
            f'<rect width="{w}" height="26" rx="7" fill="{CARD}" stroke="{EDGE}" stroke-width="1.2"/>'
            f'<circle cx="14" cy="13" r="4" fill="{color[1]}"/>'
            f'<text x="25" y="17.5" font-family="{MONO}" font-size="11.5" font-weight="700" fill="{color[0]}">{esc(text)}</text></g>'), w


class Iso:
    """Isometric projection with its origin at screen (ox, oy)."""

    def __init__(self, ox, oy):
        self.ox, self.oy = ox, oy

    def p(self, x, y, z=0):
        return (self.ox + (x - y) * C30, self.oy + (x + y) * S30 - z)

    def poly(self, pts, fill, extra=''):
        d = 'M' + ' L'.join(f'{a:.1f} {b:.1f}' for a, b in pts) + ' Z'
        # A stroke in the face's own colour softens the corners slightly.
        return f'<path d="{d}" fill="{fill}" stroke="{fill}" stroke-width="2.5" stroke-linejoin="round"{extra}/>'

    def box(self, x, y, z, w, d, h, col):
        top, left, right = col
        p = self.p
        return '\n'.join([
            self.poly([p(x, y + d, z), p(x + w, y + d, z), p(x + w, y + d, z + h), p(x, y + d, z + h)], left),
            self.poly([p(x + w, y, z), p(x + w, y + d, z), p(x + w, y + d, z + h), p(x + w, y, z + h)], right),
            self.poly([p(x, y, z + h), p(x + w, y, z + h), p(x + w, y + d, z + h), p(x, y + d, z + h)], top),
        ])

    def top_face(self, x, y, z):
        """A transform that draws 2D shapes (u right, v down) onto a top face."""
        ex, ey = self.p(x, y, z)
        return f'matrix({C30:.4f} {S30} {-C30:.4f} {S30} {ex:.1f} {ey:.1f})'

    def front_face(self, x, y, z):
        """Draws onto the face that looks down-left (the plane y = const)."""
        ex, ey = self.p(x, y, z)
        return f'matrix({C30:.4f} {S30} 0 1 {ex:.1f} {ey:.1f})'

    def side_face(self, x, y, z):
        """Draws onto the face that looks down-right (the plane x = const), u running along y."""
        ex, ey = self.p(x, y, z)
        return f'matrix({-C30:.4f} {S30} 0 1 {ex:.1f} {ey:.1f})'

    def cylinder(self, x, y, z, r, h, col):
        top, side, _ = col
        cx, cy = self.p(x, y, z)
        rx, ry = r * 1.2, r * 0.62
        return (
            f'<path d="M{cx - rx:.1f} {cy - h:.1f} V{cy:.1f} A{rx:.1f} {ry:.1f} 0 0 0 {cx + rx:.1f} {cy:.1f} V{cy - h:.1f} Z" fill="{side}"/>'
            f'<ellipse cx="{cx:.1f}" cy="{cy - h:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{top}"/>'
        )


def extruded(text, x, y, size, col, depth=4, anchor='start'):
    """A heading with a stepped 3D extrusion under it (darker copies), from the title outlines."""
    layers = ''.join(title(text, x, y + d, size, c, anchor) for d, c in
                     [(depth + 2, LIP), (depth, col[2]), (depth * .5, col[1])])
    return layers + title(text, x, y, size, col[0], anchor)


# ───────────────────────────── logos & glyphs ─────────────────────────────

# Logos drawn in black or near-black, which would vanish on the dark theme.
DARK_LOGOS = {'github', 'rust', 'nextjs', 'dokploy', 'k3s', 'aws', 'sentry', 'astro'}
DARK_FILLS = re.compile(r'fill="#(?:000|000000|161614|222c37|1a222d|26251e|252f3e|362d59|17191e)"', re.I)
_uid = [0]


def _read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def logo(key, x, y, size, color=None):
    """A tool's logo from icons/, fitted into a size×size box at (x, y)."""
    png = os.path.join(ICONS, f'{key}.png')
    if os.path.exists(png):
        with open(png, 'rb') as f:
            data = base64.b64encode(f.read()).decode()
        return f'<image x="{x}" y="{y}" width="{size}" height="{size}" href="data:image/png;base64,{data}"/>'
    src = _read(os.path.join(ICONS, f'{key}.svg'))
    vb = re.search(r'viewBox="([^"]+)"', src).group(1)
    inner = re.sub(r'^.*?<svg[^>]*>|</svg>\s*$', '', src, flags=re.S)
    inner = re.sub(r'<title>.*?</title>', '', inner)
    # Give every id a unique prefix so several logos can share one file.
    _uid[0] += 1
    pre = f'L{_uid[0]}'
    inner = re.sub(r'id="([^"]+)"', rf'id="{pre}\1"', inner)
    inner = re.sub(r'url\(#([^)]+)\)', rf'url(#{pre}\1)', inner)
    inner = re.sub(r'href="#([^"]+)"', rf'href="#{pre}\1"', inner)
    fill = color
    if key in DARK_LOGOS:
        fill = color or TEXT
        inner = DARK_FILLS.sub(f'fill="{fill}"', inner)
    g_fill = f' fill="{fill}"' if fill else ''
    return (f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="{vb}" overflow="visible">'
            f'<g{g_fill}>{inner}</g></svg>')


def glyph(name, x, y, size, color, width=2.2):
    """A Lucide line icon (icons/ui/) in one colour."""
    src = _read(os.path.join(ICONS, 'ui', f'{name}.svg'))
    inner = re.sub(r'^.*?<svg[^>]*>|</svg>\s*$', '', src, flags=re.S)
    inner = inner.replace('currentColor', color).replace('stroke-width="2"', f'stroke-width="{width}"')
    return f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="0 0 24 24" overflow="visible">{inner}</svg>'
