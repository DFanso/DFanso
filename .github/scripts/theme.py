"""Shared look for the profile README's artwork (draw_assets.py) and live
stat cards (stat_cards.py): a dark arcade theme with soft, clay-like 3D
shapes in pastel colours, drawn in plain SVG with CSS animation.

Everything is inlined (logos included) because GitHub shows these files as
images, and an SVG loaded as an image can't fetch anything.
"""
import base64
import math
import os
import random
import re
from html import escape as esc

HERE = os.path.dirname(os.path.abspath(__file__))
ICONS = os.path.join(HERE, 'icons')

SANS = "'SF Pro Rounded', ui-rounded, 'Nunito', 'Segoe UI Variable Display', 'Segoe UI', system-ui, sans-serif"
MONO = "ui-monospace, 'SF Mono', 'Cascadia Mono', 'JetBrains Mono', Consolas, 'Liberation Mono', monospace"

# Dark clay surfaces, tinted towards a night-time blue.
NIGHT = '#0e121a'       # page behind the panels
PANEL = '#151b26'       # section panels
PANEL_TOP = '#1b2231'
EDGE = '#273044'        # panel outline
CARD = '#1e2536'        # raised cards on a panel
CARD_TOP = '#252d42'
LIP = '#090c12'         # the dark underside that makes cards look raised
SLOT = '#111620'        # sunken wells (bars, inventory slots)

TEXT = '#f2f1ec'
TEXT_SOFT = '#a2abc0'
TEXT_DIM = '#677089'

# Pastel clay: (top, left face, right face).
PEACH = ('#ffd2c2', '#f5a98f', '#e48c72')
SAGE = ('#d0e8cc', '#a9d2a3', '#8cbd86')
LILAC = ('#d8dcfb', '#b8bff0', '#9aa3de')
BUTTER = ('#fbe9ae', '#f3d483', '#e3c068')
SKY = ('#cdeef0', '#9fd6db', '#7fbfc6')
ROSE = ('#fbd3dd', '#f3b3c3', '#e297aa')
SLATE = ('#434d66', '#363e55', '#2c3346')
SLATE_LIGHT = ('#58627f', '#48516b', '#3d455c')

C30, S30 = math.cos(math.pi / 6), 0.5

# Every block leaves this much clear space under itself for its shadow, so the gaps
# between blocks in the README come out the same everywhere.
PAD = 14

# The README shows every block at this share of its width (the four link tiles at a quarter of it
# each), so the blocks span exactly the dividers' dotted line; the dividers stay at full width.
NARROW = 0.88

REDUCED = '@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation: none !important; } }'


def svg(w, h, label, body, style=''):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{esc(label)}">\n<title>{esc(label)}</title>\n'
        f'<style>{style}\n{REDUCED}</style>\n{body}\n</svg>\n'
    )


def panel(w, h, glow=None, uid='p'):
    """A dark rounded panel with a soft top light, so each section reads the same on light and dark GitHub."""
    g = ''
    if glow:
        color, cx, cy, r = glow
        g = (f'<radialGradient id="{uid}glow" cx="{cx}" cy="{cy}" r="{r}"><stop offset="0" stop-color="{color}" stop-opacity=".22"/>'
             f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>')
    return (
        f'<defs><filter id="{uid}sh" x="-5%" y="-5%" width="110%" height="120%"><feDropShadow dx="0" dy="6" stdDeviation="5" '
        f'flood-color="#05040a" flood-opacity=".35"/></filter>'
        f'<linearGradient id="{uid}bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{PANEL_TOP}"/>'
        f'<stop offset="1" stop-color="{PANEL}"/></linearGradient>{g}'
        f'<pattern id="{uid}dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.1" fill="#fff" opacity=".045"/></pattern></defs>'
        f'<rect width="{w}" height="{h}" rx="30" fill="{PANEL}" filter="url(#{uid}sh)"/>'
        f'<rect width="{w}" height="{h}" rx="30" fill="url(#{uid}bg)"/>'
        f'<rect width="{w}" height="{h}" rx="30" fill="url(#{uid}dots)"/>'
        + (f'<rect width="{w}" height="{h}" rx="30" fill="url(#{uid}glow)"/>' if glow else '')
        + f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="29" fill="none" stroke="{EDGE}" stroke-width="2"/>'
        f'<path d="M30 2.5 H{w - 30}" stroke="#fff" stroke-opacity=".07" stroke-width="2" stroke-linecap="round"/>'
    )


def header(title, kicker, color, right='', x=50, y=50):
    """Section title: a small arcade tag, then the title, with optional status text on the right."""
    tag_w = 26 + len(kicker) * 7.4
    out = (f'<g transform="translate({x} {y})">'
           f'<rect y="3" width="{tag_w:.0f}" height="24" rx="12" fill="{color[2]}" opacity=".35"/>'
           f'<rect width="{tag_w:.0f}" height="24" rx="12" fill="{color[2]}" opacity=".22"/>'
           f'<rect x=".75" y=".75" width="{tag_w - 1.5:.0f}" height="22.5" rx="11.25" fill="none" stroke="{color[1]}" stroke-opacity=".55" stroke-width="1.5"/>'
           f'<text x="{tag_w / 2:.0f}" y="16.5" font-family="{MONO}" font-size="11.5" font-weight="700" letter-spacing=".5" fill="{color[0]}" text-anchor="middle">{esc(kicker)}</text>'
           f'<text y="62" font-family="{SANS}" font-size="30" font-weight="800" fill="{TEXT}">{esc(title)}</text></g>')
    if right:
        out += (f'<text x="{1000 - x}" y="{y + 16.5}" font-family="{MONO}" font-size="12" font-weight="700" letter-spacing="1.4" '
                f'fill="{TEXT_DIM}" text-anchor="end">{right}</text>')
    return out


def plate(title, kicker, color, x=0, y=0):
    """A section title on its own small raised plate, for sections drawn without a panel:
    it stays readable on GitHub's light and dark pages. Returns (svg, width)."""
    tag_w = 26 + len(kicker) * 7.4
    w = round(tag_w + 44 + len(title) * 13.2)
    return (f'<g transform="translate({x} {y})">{raised(0, 0, w, 56, 20)}'
            f'<rect x="14" y="16" width="{tag_w:.0f}" height="24" rx="12" fill="{color[2]}" fill-opacity=".28" stroke="{color[1]}" stroke-opacity=".55" stroke-width="1.5"/>'
            f'<text x="{14 + tag_w / 2:.0f}" y="32.5" font-family="{MONO}" font-size="11.5" font-weight="700" letter-spacing=".5" fill="{color[0]}" text-anchor="middle">{esc(kicker)}</text>'
            f'<text x="{tag_w + 30:.0f}" y="36.5" font-family="{SANS}" font-size="24" font-weight="800" fill="{TEXT}">{esc(title)}</text></g>'), w


def header_float(text, kicker, color, cx, y=0, size=28):
    """header_center for sections with no panel behind them: a solid tag, and the title outlined in
    the dark lip colour so it reads on GitHub's light page as well as the dark one."""
    tag_w = 26 + len(kicker) * 7.4
    return (f'<g transform="translate({cx - tag_w / 2:.1f} {y})">'
            f'<rect y="3" width="{tag_w:.0f}" height="24" rx="12" fill="{LIP}"/>'
            f'<rect width="{tag_w:.0f}" height="24" rx="12" fill="{CARD}"/>'
            f'<rect x=".75" y=".75" width="{tag_w - 1.5:.0f}" height="22.5" rx="11.25" fill="none" stroke="{color[1]}" stroke-opacity=".55" stroke-width="1.5"/>'
            f'<text x="{tag_w / 2:.0f}" y="16.5" font-family="{MONO}" font-size="11.5" font-weight="700" letter-spacing=".5" fill="{color[0]}" text-anchor="middle">{esc(kicker)}</text></g>'
            + title(text, cx, y + 30 + size, size, anchor='middle',
                    extra=f' stroke="{LIP}" stroke-width="6" stroke-linejoin="round" paint-order="stroke"'))


def chip_label(text, color, x, y):
    """A small solid label (a dot and a word) that reads on any background. Returns (svg, width)."""
    w = round(36 + len(text) * 7.4)
    return (f'<g transform="translate({x} {y})"><rect y="3" width="{w}" height="26" rx="13" fill="{LIP}"/>'
            f'<rect width="{w}" height="26" rx="13" fill="{CARD}"/>'
            f'<circle cx="15" cy="13" r="4" fill="{color[1]}"/>'
            f'<text x="26" y="17.5" font-family="{MONO}" font-size="11.5" font-weight="800" letter-spacing=".5" fill="{color[0]}">{esc(text)}</text></g>'), w


def header_center(text, kicker, color, cx, y=36, sub='', size=28):
    """A section title centred on cx: the arcade tag, the title under it, and an optional dim line."""
    tag_w = 26 + len(kicker) * 7.4
    out = (f'<g transform="translate({cx - tag_w / 2:.1f} {y})">'
           f'<rect y="3" width="{tag_w:.0f}" height="24" rx="12" fill="{color[2]}" opacity=".35"/>'
           f'<rect width="{tag_w:.0f}" height="24" rx="12" fill="{color[2]}" opacity=".22"/>'
           f'<rect x=".75" y=".75" width="{tag_w - 1.5:.0f}" height="22.5" rx="11.25" fill="none" stroke="{color[1]}" stroke-opacity=".55" stroke-width="1.5"/>'
           f'<text x="{tag_w / 2:.0f}" y="16.5" font-family="{MONO}" font-size="11.5" font-weight="700" letter-spacing=".5" fill="{color[0]}" text-anchor="middle">{esc(kicker)}</text></g>'
           + title(text, cx, y + 30 + size, size, anchor='middle'))
    if sub:
        out += (f'<text x="{cx}" y="{y + 54 + size}" font-family="{MONO}" font-size="12" font-weight="700" letter-spacing=".5" '
                f'fill="{TEXT_DIM}" text-anchor="middle">{esc(sub)}</text>')
    return out


_TITLES = None


def title(text, x, y, size, fill=TEXT, anchor='start', extra=''):
    """A title set in Fredoka (SIL Open Font License), drawn from the outlines in titles.json
    (made by make_titles.py), so no font has to load. y is the baseline. Falls back to plain text
    for a title that hasn't been outlined yet."""
    global _TITLES
    if _TITLES is None:
        import json
        with open(os.path.join(HERE, 'titles.json'), encoding='utf-8') as f:
            _TITLES = json.load(f)
    t = _TITLES.get(text)
    if t is None:
        a = {'start': 'start', 'middle': 'middle', 'end': 'end'}[anchor]
        return (f'<text x="{x}" y="{y}" font-family="{SANS}" font-size="{size}" font-weight="800" fill="{fill}" '
                f'text-anchor="{a}"{extra}>{esc(text)}</text>')
    k = size / t['upm']
    w = t['width'] * k
    x0 = x - (w / 2 if anchor == 'middle' else w if anchor == 'end' else 0)
    # Strokes are drawn in font units here, so scale any stroke width up to match.
    extra = re.sub(r'stroke-width="([\d.]+)"', lambda m: f'stroke-width="{float(m.group(1)) / k:.0f}"', extra)
    return f'<path transform="translate({x0:.1f} {y}) scale({k:.4f})" fill="{fill}"{extra} d="{t["d"]}"/>'


def shadow_filter(fid, dy=10, blur=12, opacity=0.5, color='#05040a'):
    return (
        f'<filter id="{fid}" x="-30%" y="-30%" width="160%" height="180%">'
        f'<feDropShadow dx="0" dy="{dy}" stdDeviation="{blur}" flood-color="{color}" flood-opacity="{opacity}"/></filter>'
    )


def glow_filter(fid, blur=8):
    return (f'<filter id="{fid}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{blur}" result="b"/>'
            f'<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')


def raised(x, y, w, h, rx=20, top=CARD, lip=LIP, depth=6, rim=CARD_TOP):
    """A card that sits up off the panel: dark lip below, a lighter rim along the top edge."""
    return (f'<rect x="{x}" y="{y + depth}" width="{w}" height="{h}" rx="{rx}" fill="{lip}"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{top}"/>'
            f'<rect x="{x + .75}" y="{y + .75}" width="{w - 1.5}" height="{h - 1.5}" rx="{rx - .75}" fill="none" stroke="{rim}" stroke-width="1.5"/>')


def orb(cx, cy, r, col, uid):
    """A soft clay ball with a highlight."""
    return (f'<defs><radialGradient id="{uid}" cx=".35" cy=".3" r=".75"><stop offset="0" stop-color="#fff" stop-opacity=".9"/>'
            f'<stop offset=".25" stop-color="{col[0]}"/><stop offset=".7" stop-color="{col[1]}"/><stop offset="1" stop-color="{col[2]}"/></radialGradient></defs>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#{uid})"/>')


def stars(w, h, n, seed=7, cls='tw'):
    """Twinkling specks for a night-sky background."""
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        x, y = rnd.uniform(14, w - 14), rnd.uniform(14, h - 14)
        r = rnd.choice([0.9, 1.1, 1.3, 1.8])
        c = rnd.choice(['#ffffff', LILAC[0], SKY[0], BUTTER[0], ROSE[0]])
        out.append(f'<circle class="{cls}" style="animation-delay:{-rnd.uniform(0, 4):.2f}s;animation-duration:{rnd.uniform(2.5, 5):.1f}s" '
                   f'cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{c}" opacity=".7"/>')
    return ''.join(out)


TWINKLE = '.tw { animation: tw 4s ease-in-out infinite; } @keyframes tw { 50% { opacity: .15; } }'


class Iso:
    """Isometric projection with its origin at screen (ox, oy)."""

    def __init__(self, ox, oy):
        self.ox, self.oy = ox, oy

    def p(self, x, y, z=0):
        return (self.ox + (x - y) * C30, self.oy + (x + y) * S30 - z)

    def poly(self, pts, fill, extra=''):
        d = 'M' + ' L'.join(f'{a:.1f} {b:.1f}' for a, b in pts) + ' Z'
        # A stroke in the face's own colour rounds the corners, like clay.
        return f'<path d="{d}" fill="{fill}" stroke="{fill}" stroke-width="5" stroke-linejoin="round"{extra}/>'

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

    def cylinder(self, x, y, z, r, h, col):
        top, side, _ = col
        cx, cy = self.p(x, y, z)
        rx, ry = r * 1.2, r * 0.62
        return (
            f'<path d="M{cx - rx:.1f} {cy - h:.1f} V{cy:.1f} A{rx:.1f} {ry:.1f} 0 0 0 {cx + rx:.1f} {cy:.1f} V{cy - h:.1f} Z" fill="{side}"/>'
            f'<ellipse cx="{cx:.1f}" cy="{cy - h:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{top}"/>'
        )


def pixels(rows, size, colors, x0=0, y0=0):
    out = []
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch in colors:
                out.append(f'<rect x="{x0 + i * size}" y="{y0 + j * size}" width="{size}" height="{size}" fill="{colors[ch]}"/>')
    return ''.join(out)


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
