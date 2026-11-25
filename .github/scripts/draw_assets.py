"""Draws the profile README's artwork into assets/ in a dark arcade theme:
soft, clay-like 3D shapes in pastel colours, real tool logos and a little
CSS animation. The shared palette and helpers live in theme.py; the live
GitHub stat cards are drawn by stat_cards.py in the same style.

Usage: python .github/scripts/draw_assets.py
"""
import math
import os
import re

from theme import (BUTTER, CARD, CARD_TOP, EDGE, LILAC, LIP, MONO, NARROW, PAD, PEACH, ROSE, SAGE, SANS, SKY, SLATE, SLATE_LIGHT,
                   SLOT, TEXT, TEXT_DIM, TEXT_SOFT, TWINKLE, Iso, chip_label, esc, glyph, header_center, header_float, logo, orb, panel,
                   pixels, raised, shadow_filter, stars, svg, title)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'assets')
PROJECT_ICONS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons', 'projects')

def coin(cx, cy, r, uid):
    """A gold coin, flat-on; spin it with a scaleX animation."""
    return (f'<defs><linearGradient id="{uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff3c4"/>'
            f'<stop offset=".5" stop-color="{BUTTER[1]}"/><stop offset="1" stop-color="#d6a94a"/></linearGradient></defs>'
            f'<circle cx="{cx}" cy="{cy + r * .18:.1f}" r="{r}" fill="#a87d2c"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#{uid})"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r * .68:.1f}" fill="none" stroke="#c99a3e" stroke-width="{r * .14:.1f}"/>'
            f'<rect x="{cx - r * .1:.1f}" y="{cy - r * .38:.1f}" width="{r * .2:.1f}" height="{r * .76:.1f}" rx="{r * .1:.1f}" fill="#c99a3e"/>')


# ─────────────────────────────── hero ───────────────────────────────

def hero():
    W, H = 1000, 420
    iso = Iso(712, 176)

    slab = iso.box(0, 0, 0, 260, 200, 24, SLATE)
    rim = iso.poly([iso.p(0, 0, 24), iso.p(260, 0, 24), iso.p(260, 30, 24), iso.p(0, 30, 24)], '#525d7a')

    monitor = [
        iso.box(95, 6, 24, 70, 44, 6, SLATE_LIGHT),
        iso.box(122, 20, 30, 16, 10, 40, SLATE_LIGHT),
        iso.box(36, 26, 66, 188, 10, 104, LILAC),
    ]
    face = iso.front_face(36, 36, 170)
    # A terminal running a deploy: each line types in after the one before, then the run loops.
    term_lines = [
        ('$ terraform apply', SKY[0]),
        ('  + 12 to add, 0 to destroy', TEXT_SOFT),
        ('$ kubectl rollout status', SKY[0]),
        ('  deployment "api" ready', SAGE[0]),
    ]
    tl = ''.join(f'<text class="ln l{k}" x="17" y="{27 + k * 15}" font-family="{MONO}" font-size="9.5" font-weight="700" fill="{c}">{esc(t)}</text>'
                 for k, (t, c) in enumerate(term_lines))
    game = f'''<g transform="{face}">
  <clipPath id="screen" clipPathUnits="userSpaceOnUse"><rect x="9" y="9" width="170" height="86" rx="7"/></clipPath>
  <rect x="9" y="9" width="170" height="86" rx="7" fill="#0f1420"/>
  <g clip-path="url(#screen)">
    <rect x="9" y="9" width="170" height="86" fill="url(#termbg)"/>
    {tl}
    <rect x="17" y="84" width="150" height="4" rx="2" fill="#253049"/>
    <rect class="bar" x="17" y="84" width="150" height="4" rx="2" fill="{SAGE[1]}"/>
    <rect class="cursor" x="17" y="74" width="6" height="2.5" fill="{TEXT}"/>
  </g>
  <rect class="scan" x="9" y="9" width="170" height="86" rx="7" fill="url(#scan)"/>
</g>'''

    kb = iso.box(58, 92, 24, 128, 40, 7, SLATE_LIGHT)
    keys = [f'<rect x="{6 + col * 11.8:.1f}" y="{5 + row * 11}" width="9" height="8.5" rx="2" fill="#8590b0"/>'
            for row in range(3) for col in range(10)]
    keys.append('<rect class="key" x="41.4" y="27" width="44" height="8.5" rx="2" fill="#8590b0"/>')
    keys.append(f'<rect class="key k2" x="6" y="5" width="9" height="8.5" rx="2" fill="#8590b0"/>')
    keyboard = f'{kb}<g transform="{iso.top_face(58, 92, 31)}">{"".join(keys)}</g>'

    note = (f'<g transform="{iso.top_face(196, 70, 24.5)}">'
            f'<rect x="2" y="3" width="40" height="40" rx="3" fill="{BUTTER[2]}"/>'
            f'<rect x="0" y="0" width="40" height="40" rx="3" fill="{BUTTER[0]}"/>'
            f'<path d="M7 12 H31 M7 20 H27 M7 28 H22" stroke="#d8b25a" stroke-width="2.4" stroke-linecap="round"/></g>')
    # A small server, two units high, with status lights on its front.
    rack = [iso.box(102, 146, 24 + u * 15, 64, 30, 13, SLATE_LIGHT if u else SLATE) for u in range(2)]
    leds = ''.join(
        f'<circle class="led{" blink" if (u + k) % 2 else ""}" cx="{iso.p(110 + k * 9, 176, 30.5 + u * 15)[0]:.1f}" cy="{iso.p(110 + k * 9, 176, 30.5 + u * 15)[1]:.1f}" r="2.4" fill="{c}"/>'
        for u in range(2) for k, c in enumerate([SAGE[1], SAGE[1], BUTTER[1]]))
    controller = ''.join(rack) + leds

    mug_x, mug_y = 226, 136
    mx, my = iso.p(mug_x, mug_y, 24)
    mug = (iso.cylinder(mug_x, mug_y, 24, 17, 34, PEACH)
           + f'<ellipse cx="{mx:.1f}" cy="{my - 34:.1f}" rx="14.5" ry="7.4" fill="#6b4336"/>'
           + f'<path d="M{mx + 19:.1f} {my - 26:.1f} c12 0 12 18 0 18" fill="none" stroke="{PEACH[1]}" stroke-width="6" stroke-linecap="round"/>'
           + ''.join(f'<path class="steam s{i}" d="M{mx - 6 + i * 6:.1f} {my - 44:.1f} c-6 -8 6 -12 0 -20 c-6 -8 6 -12 0 -20" fill="none" stroke="#fff" stroke-width="3.2" stroke-linecap="round"/>' for i in range(3)))
    px, py = iso.p(26, 168, 24)
    leaves = ''.join(
        f'<ellipse cx="0" cy="-22" rx="8" ry="22" fill="{c}" transform="rotate({a})"/>'
        for a, c in [(-38, SAGE[1]), (34, SAGE[1]), (-12, SAGE[0]), (14, '#c2dcb9')])
    plant = (iso.cylinder(26, 168, 24, 16, 26, ROSE)
             + f'<g class="sway" transform="translate({px:.1f} {py - 30:.1f})"><g>{leaves}</g></g>')

    gx, gy = iso.p(130, 30, 120)
    screen_glow = f'<ellipse class="glow" cx="{gx:.0f}" cy="{gy:.0f}" rx="170" ry="110" fill="url(#screenglow)"/>'
    desk = '\n'.join([slab, rim, *monitor, game, keyboard, note, controller, mug, plant])

    floaters = '\n'.join([
        f'<g class="float f1">{orb(958, 104, 22, PEACH, "ball")}</g>',
        f'<g class="float f2">{Iso(574, 82).box(0, 0, 0, 28, 28, 28, BUTTER)}</g>',
        f'<g class="float f3"><ellipse cx="946" cy="352" rx="20" ry="9" fill="none" stroke="{LILAC[1]}" stroke-width="9"/></g>',
        f'<g transform="translate(560 330)"><g class="float f4"><g class="spin">{coin(0, 0, 15, "coinA")}</g></g></g>',
    ])

    sx, sy = iso.p(130, 100, -40)
    ground = f'<ellipse class="shade" cx="{sx:.1f}" cy="{sy + 70:.1f}" rx="200" ry="26" fill="#000" opacity=".45"/>'

    # Words on the left.
    def name(text, y):
        # Set in Fredoka, with a soft clay extrusion under it.
        layers = ''.join(title(text, 62, y + d, 58, c) for d, c in [(7, '#1d2844'), (5, '#33436c'), (3, '#4b5d93')])
        return layers + title(text, 62, y, 58, 'url(#namefill)')

    def chip(x, label, col):
        w = 40 + len(label) * 8.4
        return (f'<g transform="translate({x:.0f} 314)">{raised(0, 0, round(w), 34, 17, CARD, LIP, 4, CARD_TOP)}'
                f'<circle cx="18" cy="17" r="5" fill="{col[1]}"/>'
                f'<text x="30" y="22.5" font-family="{SANS}" font-size="14" font-weight="700" fill="{col[0]}">{esc(label)}</text></g>'), w

    chips, cx_ = [], 60
    for label, col in [('DevOps Engineer', SKY), ('Backend Dev', PEACH), ('Cloud & IaC', LILAC)]:
        c, w = chip(cx_, label, col)
        chips.append(c)
        cx_ += w + 10

    # The words sit centred top to bottom in the banner.
    words = '\n'.join([
        f'<text x="62" y="78" font-family="{MONO}" font-size="15" fill="{BUTTER[0]}">&gt; Hello World! I\'m</text>',
        name('Leo', 146),
        name('Felcianas', 214),
        f'<text x="62" y="262" font-family="{SANS}" font-size="18" font-weight="600" fill="{TEXT_SOFT}">I build and run the infrastructure</text>',
        f'<text x="62" y="287" font-family="{SANS}" font-size="18" font-weight="600" fill="{TEXT_SOFT}">and backends behind real products.</text>',
        *chips,
    ])

    defs = f'''<defs>
  {shadow_filter('soft', 16, 16, 0.55)}
  <linearGradient id="termbg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#121a2b"/><stop offset="1" stop-color="#1b2740"/></linearGradient>
  <linearGradient id="scan" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".12"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <radialGradient id="screenglow"><stop offset="0" stop-color="{LILAC[1]}" stop-opacity=".35"/><stop offset="1" stop-color="{LILAC[1]}" stop-opacity="0"/></radialGradient>
  <linearGradient id="namefill" x1="0" y1="0" x2="0" y2="1"><stop offset=".2" stop-color="#fffaf3"/><stop offset="1" stop-color="{LILAC[0]}"/></linearGradient>
</defs>'''

    style = TWINKLE + '''
.desk { animation: bob 6s ease-in-out infinite; }
.shade { animation: shade 6s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }
@keyframes bob { 50% { transform: translateY(-7px); } }
@keyframes shade { 50% { transform: scale(.94); opacity: .3; } }
.glow { animation: glow 4s ease-in-out infinite; }
@keyframes glow { 50% { opacity: .65; } }
.float { animation: bob 5s ease-in-out infinite; }
.f2 { animation-duration: 6.5s; animation-delay: -2s; }
.f3 { animation-duration: 7s; animation-delay: -4s; }
.f4 { animation-duration: 4.4s; animation-delay: -1s; }
.spin { animation: spin 2.2s linear infinite; transform-box: fill-box; transform-origin: center; }
@keyframes spin { 0%, 100% { transform: scaleX(1); } 50% { transform: scaleX(.12); } }
.steam { opacity: 0; animation: steam 3.6s ease-out infinite; }
.s1 { animation-delay: 1.2s; } .s2 { animation-delay: 2.4s; }
@keyframes steam { 0% { opacity: 0; transform: translateY(6px); } 30% { opacity: .6; } 100% { opacity: 0; transform: translateY(-14px); } }
.sway > g { animation: sway 4s ease-in-out infinite; transform-origin: 0 0; }
@keyframes sway { 50% { transform: rotate(5deg); } }
.blink { animation: blink 2.4s steps(1) infinite; }
@keyframes blink { 50% { opacity: .35; } }
.key { animation: key 3.2s ease-in-out infinite; }
.k2 { animation-delay: -1.4s; }
@keyframes key { 0%, 80%, 100% { fill: #8590b0; } 88% { fill: #dfe4f7; } }
.ln { animation: type 8s steps(1) infinite both; }
.l1 { animation-delay: .8s; } .l2 { animation-delay: 2s; } .l3 { animation-delay: 3.4s; }
@keyframes type { 0% { opacity: 0; } 4%, 86% { opacity: 1; } 90%, 100% { opacity: 0; } }
.bar { animation: bar 8s ease-in-out infinite; transform-box: fill-box; transform-origin: left; }
@keyframes bar { 0% { transform: scaleX(0); } 55%, 90% { transform: scaleX(1); } 100% { transform: scaleX(0); } }
.cursor { animation: blink 1s steps(1) infinite; }
'''
    body = f'''{defs}
{panel(W, H, (LILAC[2], .75, .45, .55), 'h')}
{stars(W, H, 46)}
<g transform="translate(730 192) scale(.88) translate(-730 -222)">
{screen_glow}
{ground}
<g class="desk" filter="url(#soft)">
{desk}
</g>
{floaters}
</g>
{words}'''
    return svg(W, H + PAD, "Leo Felcianas: DevOps engineer and backend developer. I build and run the infrastructure and backends behind real products.", body, style)


# ─────────────────────────────── link tiles ───────────────────────────────

LINKS = {
    # kind: (name, kicker, handle, colour)
    'portfolio': ('Portfolio', 'Visit', 'itsme.dfanso.dev', PEACH),
    'linkedin': ('LinkedIn', 'Connect', 'in/leogavin', SKY),
    'instagram': ('Instagram', 'Follow', '@dfansoo', ROSE),
    'email': ('Email', 'Say Hi', 'leogavin123@outlook.com', BUTTER),
}


def button(kind, i):
    """A link as a clay tile that matches the stat tiles above it. The README puts the four side by
    side, each a quarter of NARROW wide (22%); tile i sits i*3px in, so the tiles fill the row edge
    to edge with 12px gaps, at the same scale as everything else."""
    name, kicker, handle, col = LINKS[kind]
    delay = i * 0.4
    W, H = 250, 108 + 6 + PAD
    x, y, w, h = i * 3, 0, 241, 108
    if kind == 'portfolio':
        icon = glyph('sparkles', x + 19, y + 16, 22, '#2e2a36', 2.3)
    else:
        icon = logo({'email': 'gmail'}.get(kind, kind), x + 20, y + 17, 20)
    style = f'''
.pop {{ animation: pop 6s ease-in-out infinite; animation-delay: {-delay}s; }}
@keyframes pop {{ 0%, 8%, 100% {{ transform: translateY(0); }} 4% {{ transform: translateY(-4px); }} }}
.shine {{ animation: shine 6s ease-in-out infinite; animation-delay: {delay}s; }}
@keyframes shine {{ 0%, 4% {{ transform: skewX(-20deg) translateX(-60px); }} 22%, 100% {{ transform: skewX(-20deg) translateX(300px); }} }}
.go {{ animation: go 2.4s ease-in-out infinite; animation-delay: {-delay}s; }}
@keyframes go {{ 50% {{ transform: translate(2px, -2px); }} }}
'''
    body = f'''<defs>{shadow_filter('soft', 6, 6, 0.35)}
<clipPath id="tile"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18"/></clipPath>
<linearGradient id="g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".12"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>
<g filter="url(#soft)">{raised(x, y, w, h, 18)}</g>
<g clip-path="url(#tile)"><rect class="shine" x="0" y="0" width="60" height="{H}" fill="url(#g)" transform="skewX(-20)"/></g>
<g class="pop"><circle cx="{x + 30}" cy="{y + 30}" r="19" fill="{col[1]}"/><circle cx="{x + 30}" cy="{y + 27}" r="19" fill="{col[0]}"/>{icon}</g>
<text x="{x + 60}" y="{y + 31}" font-family="{MONO}" font-size="11.5" font-weight="800" letter-spacing=".5" fill="{col[1]}">{kicker}</text>
<g transform="translate({x + w - 30} {y + 27})"><circle r="13" fill="{CARD_TOP}"/>
<g class="go"><path d="M-4 4 L4 -4 M-2.5 -4 H4 V2.5" fill="none" stroke="{col[1]}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></g></g>
<text x="{x + 18}" y="{y + 78}" font-family="{SANS}" font-size="21" font-weight="800" fill="{TEXT}">{name}</text>
<text x="{x + 18}" y="{y + 96}" font-family="{MONO}" font-size="11" fill="{TEXT_DIM}">{esc(handle)}</text>'''
    return svg(W, H, f'{name}: {handle}', body, style)


# ─────────────────────────────── about: quest log ───────────────────────────────

def about():
    """About me as four separate facts, each a floating clay object: what I work on, what I studied,
    what I use day to day and what I'm building on the side. No path or levels, so nothing reads as a sequence."""
    W, H = 1000, 376
    facts = [
        (PEACH, 'server', 'Working On', ['Backends, Automation', '& Infrastructure'], 'DevOps & software engineer'),
        (LILAC, 'cap', 'Studied', ['Degree In', 'Software Engineering'], 'Based in Sri Lanka'),
        (SAGE, 'workflow', 'Day To Day', ['Azure, Terraform', '& CI/CD'], 'Migrations and monitoring'),
        (SKY, 'bot', 'Also Building', ['Tools For', 'AI Agents'], 'Secrets and Telegram, kept safe'),
    ]

    def object_(kind, col):
        if kind in ('server', 'workflow', 'bot'):
            # A line icon pressed into a clay tile, the tile's darker underside giving it depth.
            return (f'<rect x="-32" y="-26" width="64" height="58" rx="16" fill="{col[2]}"/>'
                    f'<rect x="-32" y="-32" width="64" height="58" rx="16" fill="{col[0]}"/>'
                    + glyph(kind, -17, -20, 34, '#232a3a', 2.4))
        if kind == 'cap':
            return (f'<path d="M-18 -6 v12 c0 7 36 7 36 0 v-12" fill="{col[1]}"/>'
                    f'<path d="M0 -30 L36 -14 L0 2 L-36 -14 Z" fill="{col[2]}" transform="translate(0 4)"/>'
                    f'<path d="M0 -30 L36 -14 L0 2 L-36 -14 Z" fill="{col[0]}"/>'
                    f'<path d="M0 -14 L26 -4 V12" fill="none" stroke="{BUTTER[1]}" stroke-width="3" stroke-linecap="round"/>'
                    f'<circle cx="26" cy="14" r="4" fill="{BUTTER[1]}"/>')
        return Iso(0, 4).box(-17, -17, 0, 34, 34, 34, col)

    step = W / len(facts)
    xs = [step * (i + .5) for i in range(len(facts))]
    oy, floor = 180, 222  # where each object floats, and its shadow on the floor

    nodes = []
    for i, (col, kind, tag, lines, sub) in enumerate(facts):
        cx = xs[i]
        sw = 26 + len(tag) * 7.4
        shadow = f'<ellipse class="shd o{i}" cx="{cx:.0f}" cy="{floor}" rx="34" ry="7" fill="#000" opacity=".45"/>'
        text = ''.join(f'<text x="{cx:.0f}" y="{290 + j * 22}" font-family="{SANS}" font-size="18" font-weight="800" fill="{TEXT}" text-anchor="middle">{esc(t)}</text>'
                       for j, t in enumerate(lines))
        nodes.append(f'''<g>
  {shadow}
  <g transform="translate({cx:.0f} {oy})"><g class="obj o{i}">{object_(kind, col)}</g></g>
  <rect x="{cx - sw / 2:.0f}" y="246" width="{sw:.0f}" height="22" rx="11" fill="{col[2]}" fill-opacity=".2" stroke="{col[1]}" stroke-opacity=".55"/>
  <text x="{cx:.0f}" y="261" font-family="{MONO}" font-size="11" font-weight="800" letter-spacing=".5" fill="{col[0]}" text-anchor="middle">{tag}</text>
  {text}
  <text x="{cx:.0f}" y="{290 + len(lines) * 22 + 2}" font-family="{SANS}" font-size="13" fill="{TEXT_SOFT}" text-anchor="middle">{esc(sub)}</text>
</g>''')

    style = '''
.obj { animation: lift 4.5s ease-in-out infinite; }
.o1 { animation-delay: -1.1s; } .o2 { animation-delay: -2.2s; } .o3 { animation-delay: -3.3s; }
@keyframes lift { 50% { transform: translate(0, -6px); } }
.shd { animation: shd 4.5s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }
@keyframes shd { 50% { transform: scale(.85); opacity: .3; } }
'''
    body = f'''<defs>{shadow_filter('soft', 10, 12, 0.45)}</defs>
{panel(W, H, (PEACH[2], .5, 0, .6), 'a')}
{header_center('A Little About Me', 'Player Profile', PEACH, W / 2, 36)}
<g filter="url(#soft)">{''.join(nodes)}</g>'''
    return svg(W, H + PAD, 'About me. DevOps and software engineer working on backends, automation and infrastructure. Studied for a degree in Software Engineering; based in Sri Lanka. Day to day: Azure, Terraform and CI/CD, migrations and monitoring. Also building tools that let AI agents work safely, with secrets and Telegram.', body, style)


# ─────────────────────────────── featured projects ───────────────────────────────

PROJECTS = [
    # icon, name, (status, colour), kind, description (two lines), tech
    ('kv', 'LLM Key Vault', ('Author', LILAC), 'Secrets Broker · DFanso',
     ['A local secrets broker for AI coding agents: they use your', 'API keys, tokens and DB passwords without seeing them.'],
     ['Rust', 'MCP', 'Postgres', 'Redis']),
    ('telegram-mcp', 'Telegram MCP', ('Contributor', SKY), 'MCP Server · iddhi-sulakshana',
     ['Telegram for Claude Code through one always-on daemon,', 'shared by every session. Sends only what you allow.'],
     ['TypeScript', 'Bun', 'MCP']),
    ('server-dash', 'Server Dash', ('Author', SAGE), 'Dashboard · Self-Hosted',
     ['A self-hosted dashboard for a V2rayA hotspot: CPU, memory,', 'throughput and V2rayA status, shipped as one binary.'],
     ['Rust', 'React', 'TypeScript']),
    ('bridge-relay', 'Bridge Relay', ('Author', PEACH), 'Claude Code · SSH Relay',
     ['Joins Claude Code session-bridge across machines over', 'SSH, so a remote session shows up as a local peer.'],
     ['Python', 'SSH', 'Claude Code']),
]


def app_icon(key, s):
    """A project's own icon (icons/projects/) as a raised app tile, s×s at the origin."""
    r = round(s * .26, 1)
    tile = f'<rect width="{s}" height="{s}" rx="{r}"'
    out = f'<rect y="5" width="{s}" height="{s}" rx="{r}" fill="{LIP}"/><clipPath id="ic-{key}">{tile}/></clipPath><g clip-path="url(#ic-{key})">'
    if key == 'bridge-relay':
        # No icon of its own: a cable glyph on a tile in the card's colour.
        out += (f'<linearGradient id="br" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{PEACH[0]}"/><stop offset="1" stop-color="{PEACH[2]}"/></linearGradient>'
                f'{tile} fill="url(#br)"/>' + glyph('cable', s * .22, s * .22, s * .56, '#232a3a', 2.2))
    elif key == 'server-dash':
        # Its own favicon (512 units), with its ids prefixed so they can't clash with the card's.
        with open(os.path.join(PROJECT_ICONS, 'server-dash.svg'), encoding='utf-8') as f:
            inner = re.sub(r'^.*?<svg[^>]*>|</svg>\s*$', '', f.read(), flags=re.S)
        inner = re.sub(r'id="([^"]+)"', r'id="sd\1"', inner)
        inner = re.sub(r'url\(#([^)]+)\)', r'url(#sd\1)', inner)
        out += f'<svg width="{s}" height="{s}" viewBox="0 0 512 512">{inner}</svg>'
    elif key == 'telegram-mcp':
        with open(os.path.join(PROJECT_ICONS, 'telegram-mcp.svg'), encoding='utf-8') as f:
            plane = re.search(r'<path [^>]*/>', f.read()).group(0).replace('#1B92D1', '#fff')
        out += (f'<linearGradient id="tg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#41b4e6"/><stop offset="1" stop-color="#1b92d1"/></linearGradient>'
                f'{tile} fill="url(#tg)"/><svg x="{s * .2:.1f}" y="{s * .22:.1f}" width="{s * .58:.1f}" height="{s * .58:.1f}" viewBox="0 0 100 100">{plane}</svg>')
    else:
        with open(os.path.join(PROJECT_ICONS, f'{key}.svg'), encoding='utf-8') as f:
            inner = re.sub(r'^.*?<svg[^>]*>|</svg>\s*$', '', f.read(), flags=re.S)
        inner = re.sub(r'<!--.*?-->', '', inner, flags=re.S).replace('id="tile"', 'id="kvtile"').replace('url(#tile)', 'url(#kvtile)')
        out += f'<svg width="{s}" height="{s}" viewBox="2 2 60 60">{inner}</svg>'
    # A soft gloss and rim so every icon reads as the same clay tile.
    out += (f'</g><rect width="{s}" height="{s / 2:.0f}" rx="{r}" fill="#fff" opacity=".07"/>'
            f'<rect x=".75" y=".75" width="{s - 1.5}" height="{s - 1.5}" rx="{r - .75}" fill="none" stroke="#fff" stroke-opacity=".14" stroke-width="1.5"/>')
    return out


def projects_title():
    """The Featured Projects heading on its own, so each project card below it can be a link."""
    W, H = 1000, 66 + PAD
    return svg(W, H, 'Featured projects', header_float('Featured Projects', 'Quest Log', BUTTER, W / 2, 0))


def project_card(i):
    """One featured project as a clay card. The README shows two side by side, each half of NARROW
    wide; card i%2 sits 6px in, so a pair fills the row edge to edge with a 12px gap."""
    key, name, (status, col), kind, desc, tech = PROJECTS[i]
    W, w, h = 500, 494, 206
    H = h + 6 + PAD
    x = (i % 2) * 6
    delay = i * .5
    sw = 26 + len(status) * 7.4
    chips, cx = [], x + 22
    for t in tech:
        tw = round(20 + len(t) * 6.9)
        chips.append(f'<rect x="{cx}" y="168" width="{tw}" height="22" rx="11" fill="{SLOT}" stroke="{EDGE}" stroke-width="1.5"/>'
                     f'<text x="{cx + tw / 2:.1f}" y="183" font-family="{MONO}" font-size="11" font-weight="700" fill="{TEXT_SOFT}" text-anchor="middle">{esc(t)}</text>')
        cx += tw + 8
    lines = ''.join(f'<text x="{x + 22}" y="{132 + j * 20}" font-family="{SANS}" font-size="13.5" fill="{TEXT_SOFT}">{esc(t)}</text>'
                    for j, t in enumerate(desc))
    style = f'''
.bob {{ animation: bob 4.5s ease-in-out infinite; animation-delay: {-delay}s; }}
@keyframes bob {{ 50% {{ transform: translateY(-4px); }} }}
.shine {{ animation: shine 7s ease-in-out infinite; animation-delay: {delay}s; }}
@keyframes shine {{ 0%, 4% {{ transform: skewX(-20deg) translateX(-80px); }} 24%, 100% {{ transform: skewX(-20deg) translateX(620px); }} }}
.go {{ animation: go 2.4s ease-in-out infinite; animation-delay: {-delay}s; }}
@keyframes go {{ 50% {{ transform: translate(2px, -2px); }} }}
'''
    body = f'''<defs>{shadow_filter('soft', 6, 6, 0.35)}
<clipPath id="card"><rect x="{x}" y="0" width="{w}" height="{h}" rx="22"/></clipPath>
<linearGradient id="g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".08"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>
<g filter="url(#soft)">{raised(x, 0, w, h, 22)}</g>
<g clip-path="url(#card)"><rect class="shine" x="0" y="0" width="80" height="{H}" fill="url(#g)" transform="skewX(-20)"/></g>
<g transform="translate({x + 22} 22)"><g class="bob">{app_icon(key, 68)}</g></g>
<rect x="{x + 108}" y="22" width="{sw:.0f}" height="22" rx="11" fill="{col[2]}" fill-opacity=".22" stroke="{col[1]}" stroke-opacity=".6" stroke-width="1.5"/>
<text x="{x + 108 + sw / 2:.0f}" y="37" font-family="{MONO}" font-size="11" font-weight="800" letter-spacing=".5" fill="{col[0]}" text-anchor="middle">{esc(status)}</text>
<text x="{x + 108}" y="74" font-family="{SANS}" font-size="24" font-weight="800" fill="{TEXT}">{esc(name)}</text>
<text x="{x + 108}" y="95" font-family="{MONO}" font-size="11.5" fill="{TEXT_DIM}">{esc(kind)}</text>
<g transform="translate({x + w - 32} 33)"><circle r="14" fill="{CARD_TOP}"/>
<g class="go"><path d="M-4 4 L4 -4 M-2.5 -4 H4 V2.5" fill="none" stroke="{col[1]}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></g></g>
{lines}
{''.join(chips)}'''
    label = f'{name} ({status}): {kind}. {" ".join(desc)} Built with {", ".join(tech)}.'
    return svg(W, H, label, body, style)


# ─────────────────────────────── stack: inventory ───────────────────────────────

GROUPS = [
    ('Cloud & Deploy', SKY, [('AWS', 'aws'), ('Azure', 'azure'), ('Cloudflare', 'cloudflare'), ('Docker', 'docker'),
                             ('Kubernetes', 'kubernetes'), ('K3s', 'k3s'), ('Dokploy', 'dokploy')]),
    ('Backend & Data', PEACH, [('NestJS', 'nestjs'), ('Node.js', 'nodejs'), ('Go', 'go'), ('Python', 'python'), ('Rust', 'rust'),
                               ('C# / .NET', 'csharp'), ('PostgreSQL', 'postgresql'), ('MongoDB', 'mongodb'), ('Redis', 'redis')]),
    ('Frontend', ROSE, [('React', 'react'), ('Next.js', 'nextjs'), ('Astro', 'astro'), ('Tailwind', 'tailwind')]),
    ('DevOps & IaC', SAGE, [('Terraform', 'terraform'), ('GH Actions', 'github-actions'), ('Jenkins', 'jenkins'), ('ArgoCD', 'argocd'),
                            ('Prometheus', 'prometheus'), ('Grafana', 'grafana'), ('Sentry', 'sentry')]),
    ('AI & Workflow', LILAC, [('Claude', 'claude'), ('Git', 'git'), ('GitHub', 'github'), ('ClickUp', 'clickup')]),
]
PER_ROW = 9


def stack():
    """The toolbox as loose inventory slots (no panel), PER_ROW to a row; a group with more
    tools than that wraps onto another row."""
    W, gap, sh = 1000, 14, 100
    sw = (W - (PER_ROW - 1) * gap) / PER_ROW
    title = header_float('My Toolbox', 'Inventory', SKY, W / 2, 0)
    out, y, n = [], 102, 0
    for name_, col, tools in GROUPS:
        _, cw = chip_label(name_, col, 0, 0)
        chip, _ = chip_label(name_, col, round((W - cw) / 2), y)
        rule = f'stroke="{EDGE}" stroke-width="1.5" stroke-dasharray="2 6" stroke-linecap="round"'
        out.append(chip + f'<path d="M0 {y + 14} H{(W - cw) / 2 - 14:.0f} M{(W + cw) / 2 + 14:.0f} {y + 14} H{W}" {rule}/>')
        y += 44
        for i, (name, key) in enumerate(tools):
            if i and i % PER_ROW == 0:
                y += sh + 6 + gap
            # A short last row sits centred.
            left = len(tools) - i + i % PER_ROW
            row_n = min(PER_ROW, left)
            x = (W - (row_n * sw + (row_n - 1) * gap)) / 2 + (i % PER_ROW) * (sw + gap)
            out.append(f'''<g transform="translate({x:.1f} {y})">
  {raised(0, 0, round(sw, 1), sh, 18)}
  <rect x="8" y="8" width="{sw - 16:.1f}" height="60" rx="13" fill="{SLOT}"/>
  <rect x="8.75" y="8.75" width="{sw - 17.5:.1f}" height="58.5" rx="12.25" fill="none" stroke="{col[2]}" stroke-opacity=".35" stroke-width="1.5"/>
  <ellipse cx="{sw / 2:.1f}" cy="60" rx="18" ry="3.5" fill="#000" opacity=".5"/>
  <g class="item" style="animation-delay:{-n * .37:.2f}s">{logo(key, round(sw / 2 - 17, 1), 21, 34)}</g>
  <clipPath id="c{n}"><rect x="8" y="8" width="{sw - 16:.1f}" height="60" rx="13"/></clipPath>
  <g clip-path="url(#c{n})"><rect class="glint" style="animation-delay:{n * .2:.2f}s" x="-30" y="0" width="22" height="80" fill="#fff" opacity=".13" transform="skewX(-22)"/></g>
  <text x="{sw / 2:.1f}" y="88" font-family="{SANS}" font-size="12.5" font-weight="700" fill="{TEXT}" text-anchor="middle">{esc(name)}</text>
</g>''')
            n += 1
        y += sh + 6 + 30
    H = y - 30 + PAD
    style = '''
.item { animation: hover 3.6s ease-in-out infinite; }
@keyframes hover { 50% { transform: translateY(-3px); } }
.glint { animation: glint 9s ease-in-out infinite; }
@keyframes glint { 0% { transform: skewX(-22deg) translateX(0); } 8%, 100% { transform: skewX(-22deg) translateX(220px); } }
'''
    body = f'''<defs>{shadow_filter('soft', 6, 6, 0.35)}</defs>
<g filter="url(#soft)">{title}{''.join(out)}</g>'''
    names = ', '.join(name for _, _, tools in GROUPS for name, _ in tools)
    return svg(W, H, f'My toolbox: {names}', body, style)


# ─────────────────────────────── divider & footer ───────────────────────────────

def divider():
    """A plain dotted rule as wide as the blocks around it (they're shown at NARROW of the README's
    width), centred between them: the block above leaves PAD under itself, which shrinks with it."""
    W = 1000
    pad = round(PAD * NARROW)
    H = 10 + 10 + pad
    x0 = W * (1 - NARROW) / 2
    body = f'<path d="M{x0:g} 10 H{W - x0:g}" stroke="{LILAC[2]}" stroke-opacity=".55" stroke-width="2.5" stroke-linecap="round" stroke-dasharray="1 9"/>'
    return svg(W, H, '', body)


def footer():
    """A centred continue screen with an arcade button on the left and a joystick on the right."""
    W, H = 1000, 260
    # Arcade button, left.
    biso = Iso(150, 104)
    base_l = biso.box(-50, -50, 0, 100, 100, 20, SLATE)
    bx, by = biso.p(0, 0, 20)
    button_ = (f'<g class="btn"><ellipse cx="{bx:.1f}" cy="{by + 4:.1f}" rx="38" ry="20" fill="#c76a82"/>'
               f'<ellipse cx="{bx:.1f}" cy="{by - 5:.1f}" rx="38" ry="20" fill="{ROSE[1]}"/>'
               f'<ellipse cx="{bx - 9:.1f}" cy="{by - 10:.1f}" rx="15" ry="6" fill="#fff" opacity=".45"/></g>')
    # Joystick, right.
    jiso = Iso(850, 104)
    base_r = jiso.box(-50, -50, 0, 100, 100, 20, SLATE)
    jx, jy = jiso.p(0, 0, 20)
    stick = (f'<ellipse cx="{jx:.1f}" cy="{jy:.1f}" rx="20" ry="10" fill="{SLATE[2]}"/>'
             f'<g class="stick" style="transform-origin:{jx:.1f}px {jy:.1f}px">'
             f'<rect x="{jx - 5:.1f}" y="{jy - 52:.1f}" width="10" height="52" rx="5" fill="#2b2640"/>'
             f'{orb(round(jx, 1), round(jy - 58, 1), 17, PEACH, "knob")}</g>')
    halo = (f'<ellipse class="halo" cx="{bx:.0f}" cy="{by + 20:.0f}" rx="120" ry="70" fill="url(#halo)"/>'
            f'<ellipse class="halo h2" cx="{jx:.0f}" cy="{jy + 20:.0f}" rx="120" ry="70" fill="url(#halo)"/>')
    sparks = ''.join(
        f'<path d="M{bx + 58 * math.cos(a):.0f} {by - 5 + 34 * math.sin(a):.0f} l{11 * math.cos(a):.0f} {7 * math.sin(a):.0f}" stroke="{BUTTER[1]}" stroke-width="3" stroke-linecap="round"/>'
        for a in [math.radians(d) for d in (200, 235, 270, 305, 340)])
    cx = W / 2
    cont_x = cx - 70  # "CONTINUE?" plus a gap and one digit, centred as a group
    digits = ''.join(f'<text class="d" style="animation-delay:{k - 10}s{";opacity:1" if k == 0 else ""}" x="{cont_x + 128:.0f}" y="152" '
                     f'font-family="{MONO}" font-size="20" font-weight="800" fill="{ROSE[0]}">{9 - k}</text>' for k in range(10))
    style = TWINKLE + '''
.btn { animation: push 3s ease-in-out infinite; }
@keyframes push { 0%, 70%, 100% { transform: translateY(0); } 80% { transform: translateY(7px); } }
.stick { animation: stick 3s ease-in-out infinite; }
@keyframes stick { 0%, 100% { transform: rotate(0); } 25% { transform: rotate(-12deg); } 60% { transform: rotate(10deg); } }
.spark { opacity: 0; animation: spark 3s ease-out infinite; transform-box: fill-box; transform-origin: center; }
@keyframes spark { 0%, 78% { opacity: 0; transform: scale(.6); } 85% { opacity: 1; } 100% { opacity: 0; transform: scale(1.25); } }
.halo { animation: halo 3s ease-in-out infinite; }
.h2 { animation-delay: -1.5s; }
@keyframes halo { 0%, 70%, 100% { opacity: .45; } 82% { opacity: 1; } }
.caret, .coin { animation: caret 1s steps(1) infinite; }
@keyframes caret { 50% { opacity: 0; } }
.d { opacity: 0; animation: cd 10s steps(1) infinite; }
@keyframes cd { 0% { opacity: 1; } 10%, 100% { opacity: 0; } }
'''
    body = f'''<defs>{shadow_filter('soft', 12, 12, 0.55)}
<radialGradient id="halo"><stop offset="0" stop-color="{ROSE[1]}" stop-opacity=".28"/><stop offset="1" stop-color="{ROSE[1]}" stop-opacity="0"/></radialGradient></defs>
{panel(W, H, (ROSE[2], .5, .5, .6), 'f')}
{stars(W, H, 22, 11)}
{halo}
<g class="spark">{sparks}</g>
<g filter="url(#soft)">{base_l}{button_}{base_r}{stick}</g>
<text x="{cx}" y="62" font-family="{MONO}" font-size="13" font-weight="800" letter-spacing=".5" fill="{ROSE[1]}" text-anchor="middle">All Checks Passed</text>
{title('Thanks For Stopping By!', cx, 110, 32, anchor='middle')}
<text x="{cont_x:.0f}" y="152" font-family="{MONO}" font-size="20" font-weight="800" fill="{BUTTER[0]}">Continue?</text>{digits}
<text x="{cx}" y="188" font-family="{SANS}" font-size="16" font-weight="600" fill="{TEXT_SOFT}" text-anchor="middle">Visit my site to see what I'm building lately</text>
<text x="{cx}" y="220" font-family="{MONO}" font-size="14" fill="{PEACH[1]}" text-anchor="middle">itsme.dfanso.dev<tspan class="caret" fill="{TEXT}">_</tspan></text>
<text class="coin" x="{bx:.0f}" y="236" font-family="{MONO}" font-size="11" font-weight="800" letter-spacing=".5" fill="{BUTTER[1]}" text-anchor="middle">Deploy</text>
<text x="{jx:.0f}" y="236" font-family="{MONO}" font-size="11" font-weight="800" letter-spacing=".5" fill="{TEXT_DIM}" text-anchor="middle">Rollback?</text>'''
    return svg(W, H + PAD, "Thanks for stopping by! Visit my website to see what I'm building lately.", body, style)


def main():
    files = {
        'hero.svg': hero(),
        'about.svg': about(),
        'stack.svg': stack(),
        'divider.svg': divider(),
        'footer.svg': footer(),
        **{f'btn-{kind}.svg': button(kind, i) for i, kind in enumerate(LINKS)},
        'projects.svg': projects_title(),
        **{f'project-{p[0]}.svg': project_card(i) for i, p in enumerate(PROJECTS)},
    }
    os.makedirs(OUT, exist_ok=True)
    for name, text in files.items():
        with open(os.path.join(OUT, name), 'w', encoding='utf-8', newline='\n') as f:
            f.write(text)
        print(f'{name}: {len(text):,} bytes')


if __name__ == '__main__':
    main()
