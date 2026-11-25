"""Draws the profile README's artwork into assets/ in a dark terminal / editor
theme: every block is a window that stands off the page, the illustrations are
isometric 3D (a workstation, server racks, containers), the type is monospace
and the headings are shell commands. The shared palette and helpers live in
theme.py; the live GitHub stat cards are drawn by stat_cards.py in the same style.

Usage: python .github/scripts/draw_assets.py
"""
import os
import re

from theme import (AMBER, BLINK, BLUE, CARD, CARD_TOP, CYAN, EDGE, GREEN, LIP, MONO, NARROW, PAD, PANEL_TOP, PURPLE, RED, SLOT,
                   STEEL, STEEL_LIGHT, TEXT, TEXT_DIM, TEXT_SOFT, Iso, badge, chip_label, command, esc, extruded, glyph, logo, plate,
                   raised, shadow_filter, svg, title, window)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'assets')
PROJECT_ICONS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons', 'projects')

NAME = ('#e6ecff', BLUE[1], '#3d5aa8')
ARROW = 'M-4 4 L4 -4 M-2.5 -4 H4 V2.5'


def prompt(x, y, cmd='', size=15, path='~'):
    """`leo@dfanso:~$ cmd` in the usual colours."""
    return (f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" font-weight="700">'
            f'<tspan fill="{GREEN[1]}">leo@dfanso</tspan><tspan fill="{TEXT_DIM}">:</tspan><tspan fill="{BLUE[1]}">{esc(path)}</tspan>'
            f'<tspan fill="{TEXT_DIM}">$ </tspan><tspan fill="{TEXT}">{esc(cmd)}</tspan></text>')


def rack(iso, x, y, z, units, w=70, d=40, uh=15, cls='led'):
    """A small server rack: `units` boxes stacked, each with a vent slot and status lights on its
    front face (the face looking down-left)."""
    out = []
    for u in range(units):
        z0 = z + u * uh
        out.append(iso.box(x, y, z0, w, d, uh - 1.5, STEEL_LIGHT if u % 2 else STEEL))
        lights = ''.join(f'<circle class="{cls}{" blink" if (u + k) % 3 == 1 else ""}" cx="{8 + k * 7}" cy="{(uh - 1.5) / 2:.1f}" r="2.1" '
                         f'fill="{c[1]}"/>' for k, c in enumerate((GREEN, GREEN, AMBER if u == 1 else GREEN)))
        out.append(f'<g transform="{iso.front_face(x, y + d, z0 + uh - 1.5)}">'
                   f'<rect x="32" y="{(uh - 1.5) / 2 - 1.5:.1f}" width="{w - 40}" height="3" rx="1.5" fill="#1a1d2b"/>{lights}</g>')
    return ''.join(out)


def container(iso, x, y, z, s, col):
    """A shipping-container cube with ribs on its front and side faces."""
    ribs = ''.join(f'<path d="M{s * k / 5:.1f} 3 V{s - 3:.1f}" stroke="{col[2]}" stroke-width="2" stroke-linecap="round" opacity=".7"/>' for k in range(1, 5))
    return (iso.box(x, y, z, s, s, s, col)
            + f'<g transform="{iso.front_face(x, y + s, z + s)}">{ribs}</g>'
            + f'<g transform="{iso.side_face(x + s, y, z + s)}">{ribs}</g>')


# ─────────────────────────────── hero ───────────────────────────────

def hero():
    W, H = 1000, 420
    iso = Iso(712, 176)

    slab = iso.box(0, 0, 0, 260, 200, 24, STEEL)
    rim = iso.poly([iso.p(0, 0, 24), iso.p(260, 0, 24), iso.p(260, 30, 24), iso.p(0, 30, 24)], '#535c80')

    monitor = [
        iso.box(95, 6, 24, 70, 44, 6, STEEL_LIGHT),
        iso.box(122, 20, 30, 16, 10, 36, STEEL_LIGHT),
        iso.box(22, 26, 60, 216, 10, 124, ('#3d4462', '#2a2f45', '#323855')),
    ]
    face = iso.front_face(22, 36, 184)
    # A terminal running a deploy: each line types in after the one before, the pipeline stages
    # turn green one by one, then the run loops. The base state (no animation) is the finished run.
    term = [
        ('$ terraform apply -auto-approve', TEXT),
        ('  Apply complete! 12 added.', GREEN[1]),
        ('$ kubectl rollout status api', TEXT),
        ('  deployment "api" rolled out', GREEN[1]),
        ('$ git push origin main', TEXT),
    ]
    tl = ''.join(f'<text class="ln l{k}" x="17" y="{24 + k * 14.5}" font-family="{MONO}" font-size="8.2" font-weight="700" fill="{c}">'
                 + (f'<tspan fill="{GREEN[1]}">$</tspan>{esc(t[1:])}' if t.startswith('$') else esc(t)) + '</text>'
                 for k, (t, c) in enumerate(term))
    stages = ''.join(
        f'<g class="ln l{5 + k}"><rect class="st s{k}" x="{17 + k * 46}" y="95" width="40" height="15" rx="3" fill="{GREEN[2]}"/>'
        f'<text x="{21 + k * 46}" y="105.5" font-family="{MONO}" font-size="7.4" font-weight="800" fill="#10131c">{n}</text>'
        f'<path d="M{46 + k * 46} 102.5 l2 2 l4 -4.5" fill="none" stroke="#10131c" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></g>'
        for k, n in enumerate(('build', 'test', 'scan', 'ship')))
    screen = f'''<g transform="{face}">
  <clipPath id="screen" clipPathUnits="userSpaceOnUse"><rect x="8" y="8" width="200" height="108" rx="6"/></clipPath>
  <rect x="8" y="8" width="200" height="108" rx="6" fill="#11121a"/>
  <g clip-path="url(#screen)">
    <rect x="8" y="8" width="200" height="108" fill="url(#termbg)"/>
    {tl}
    {stages}
  </g>
  <rect x="8" y="8" width="200" height="108" rx="6" fill="url(#scan)"/>
</g>'''

    kb = iso.box(58, 96, 24, 128, 40, 7, STEEL_LIGHT)
    keys = [f'<rect x="{6 + col * 11.8:.1f}" y="{5 + row * 11}" width="9" height="8.5" rx="2" fill="#6b7499"/>'
            for row in range(3) for col in range(10)]
    keys.append('<rect class="key" x="41.4" y="27" width="44" height="8.5" rx="2" fill="#6b7499"/>')
    keys.append('<rect class="key k2" x="100.6" y="16" width="9" height="8.5" rx="2" fill="#6b7499"/>')
    keyboard = f'{kb}<g transform="{iso.top_face(58, 96, 31)}">{"".join(keys)}</g>'

    server = rack(iso, 150, 150, 24, 3, 70, 40)
    boxes = container(iso, 14, 150, 24, 30, CYAN) + container(iso, 14, 150, 54, 30, BLUE) + container(iso, 48, 160, 24, 26, PURPLE)

    mug_x, mug_y = 236, 112
    mx, my = iso.p(mug_x, mug_y, 24)
    mug = (iso.cylinder(mug_x, mug_y, 24, 15, 30, AMBER)
           + f'<ellipse cx="{mx:.1f}" cy="{my - 30:.1f}" rx="12.5" ry="6.4" fill="#4a3424"/>'
           + f'<path d="M{mx + 17:.1f} {my - 23:.1f} c11 0 11 16 0 16" fill="none" stroke="{AMBER[1]}" stroke-width="5" stroke-linecap="round"/>'
           + ''.join(f'<path class="steam s{i}" d="M{mx - 5 + i * 5:.1f} {my - 38:.1f} c-5 -7 5 -10 0 -17 c-5 -7 5 -10 0 -17" fill="none" stroke="#fff" stroke-width="2.8" stroke-linecap="round" opacity=".35"/>' for i in range(3)))

    gx, gy = iso.p(130, 30, 120)
    screen_glow = f'<ellipse class="glow" cx="{gx:.0f}" cy="{gy:.0f}" rx="180" ry="115" fill="url(#screenglow)"/>'
    desk = '\n'.join([slab, rim, *monitor, screen, keyboard, boxes, server, mug])

    floaters = '\n'.join([
        f'<g class="float f1">{extruded("</>", 936, 112, 34, PURPLE, 4, "middle")}</g>',
        f'<g class="float f2">{extruded("{ }", 566, 98, 32, AMBER, 4, "middle")}</g>',
        f'<g class="float f3">{container(Iso(944, 318), 0, 0, 0, 24, CYAN)}</g>',
        f'<g class="float f4"><circle cx="562" cy="336" r="17" fill="{GREEN[2]}"/><circle cx="562" cy="332" r="17" fill="{GREEN[1]}"/>'
        f'<path d="M554 332 l5.5 5.5 l10 -11" fill="none" stroke="#10131c" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/></g>',
    ])

    sx, sy = iso.p(130, 100, -40)
    ground = f'<ellipse class="shade" cx="{sx:.1f}" cy="{sy + 70:.1f}" rx="200" ry="26" fill="#000" opacity=".45"/>'

    def tab(x, label, ext, col, active):
        """An editor tab: a file-type dot, the role as a file name, the active one lit along its top."""
        text = f'{label}{ext}'
        w = round(38 + len(text) * 7.8)
        top = (f'<rect x="0" y="0" width="{w}" height="3" rx="1.5" fill="{col[1]}"/>' if active else '')
        return (f'<g transform="translate({x} 320)">{raised(0, 0, w, 34, 8, CARD_TOP if active else CARD, LIP, 5, EDGE)}{top}'
                f'<circle cx="16" cy="17" r="4.5" fill="{col[1]}"/>'
                f'<text x="28" y="21.5" font-family="{MONO}" font-size="13" font-weight="700" fill="{TEXT if active else TEXT_SOFT}">{esc(label)}'
                f'<tspan fill="{TEXT_DIM}">{esc(ext)}</tspan></text></g>'), w

    tabs, tx = [], 56
    for label, ext, col, active in [('devops', '.tf', PURPLE, True), ('backend', '.ts', BLUE, False), ('cloud-iac', '.yaml', CYAN, False)]:
        t, w = tab(tx, label, ext, col, active)
        tabs.append(t)
        tx += w + 8

    words = '\n'.join([
        prompt(56, 92, 'whoami'),
        extruded('Leo', 56, 162, 60, NAME, 4),
        extruded('Felcianas', 56, 230, 60, NAME, 4),
        f'<text x="56" y="272" font-family="{MONO}" font-size="15" fill="{TEXT_DIM}">// DevOps engineer &amp; backend developer.</text>',
        f'<text x="56" y="295" font-family="{MONO}" font-size="15" fill="{TEXT_SOFT}">I build and run the infra behind real products.</text>',
        *tabs,
    ])

    defs = f'''<defs>
  {shadow_filter('soft', 16, 16, 0.55)}
  <linearGradient id="termbg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#14161f"/><stop offset="1" stop-color="#1a1d2b"/></linearGradient>
  <linearGradient id="scan" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".08"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <radialGradient id="screenglow"><stop offset="0" stop-color="{BLUE[1]}" stop-opacity=".3"/><stop offset="1" stop-color="{BLUE[1]}" stop-opacity="0"/></radialGradient>
</defs>'''

    style = BLINK + f'''
.desk {{ animation: bob 6s ease-in-out infinite; }}
.shade {{ animation: shade 6s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }}
@keyframes bob {{ 50% {{ transform: translateY(-7px); }} }}
@keyframes shade {{ 50% {{ transform: scale(.94); opacity: .3; }} }}
.glow {{ animation: glow 4s ease-in-out infinite; }}
@keyframes glow {{ 50% {{ opacity: .6; }} }}
.float {{ animation: bob 5s ease-in-out infinite; }}
.f2 {{ animation-duration: 6.5s; animation-delay: -2s; }}
.f3 {{ animation-duration: 7s; animation-delay: -4s; }}
.f4 {{ animation-duration: 4.4s; animation-delay: -1s; }}
.steam {{ opacity: 0; animation: steam 3.6s ease-out infinite; }}
.s1 {{ animation-delay: 1.2s; }} .s2 {{ animation-delay: 2.4s; }}
@keyframes steam {{ 0% {{ opacity: 0; transform: translateY(6px); }} 30% {{ opacity: .45; }} 100% {{ opacity: 0; transform: translateY(-14px); }} }}
.blink {{ animation: blink 2.4s steps(1) infinite; }}
@keyframes blink {{ 50% {{ opacity: .3; }} }}
.key {{ animation: key 3.2s ease-in-out infinite; }}
.k2 {{ animation-delay: -1.4s; }}
@keyframes key {{ 0%, 80%, 100% {{ fill: #6b7499; }} 88% {{ fill: {BLUE[0]}; }} }}
.ln {{ animation: type 10s steps(1) infinite both; }}
.l1 {{ animation-delay: .7s; }} .l2 {{ animation-delay: 1.6s; }} .l3 {{ animation-delay: 2.6s; }} .l4 {{ animation-delay: 3.5s; }}
.l5 {{ animation-delay: 4.1s; }} .l6 {{ animation-delay: 4.7s; }} .l7 {{ animation-delay: 5.3s; }} .l8 {{ animation-delay: 5.9s; }}
@keyframes type {{ 0% {{ opacity: 0; }} 3%, 88% {{ opacity: 1; }} 92%, 100% {{ opacity: 0; }} }}
.st {{ animation: stage 10s steps(1) infinite both; }}
.s1.st {{ animation-delay: 4.7s; }} .s2.st {{ animation-delay: 5.3s; }} .s3.st {{ animation-delay: 5.9s; }} .s0.st {{ animation-delay: 4.1s; }}
@keyframes stage {{ 0% {{ fill: {AMBER[1]}; }} 5%, 100% {{ fill: {GREEN[1]}; }} }}
'''
    body = f'''{defs}
{window(W, H, 'leo@dfanso: ~ — zsh', 'h', glow=(BLUE[2], .75, .5, .55))}
<g transform="translate(736 214) scale(.84) translate(-730 -222)">
{screen_glow}
{ground}
<g class="desk" filter="url(#soft)">
{desk}
</g>
{floaters}
</g>
{words}'''
    return svg(W, H + PAD + 8, "Leo Felcianas: DevOps engineer and backend developer. I build and run the infrastructure and backends behind real products.", body, style)


# ─────────────────────────────── link tiles ───────────────────────────────

LINKS = {
    # kind: (name, verb, handle, colour)
    'portfolio': ('portfolio', 'open', 'itsme.dfanso.dev', GREEN),
    'linkedin': ('linkedin', 'connect', 'in/leogavin', BLUE),
    'instagram': ('instagram', 'follow', '@dfansoo', PURPLE),
    'email': ('email', 'mail', 'leogavin123@outlook.com', AMBER),
}


def button(kind, i):
    """A link as a small terminal window. The README puts the four side by side, each a quarter of
    NARROW wide (22%); tile i sits i*3px in, so the tiles fill the row edge to edge with 12px gaps,
    at the same scale as everything else."""
    name, verb, handle, col = LINKS[kind]
    delay = i * 0.4
    W, H = 250, 112 + 8 + PAD
    x, y, w, h = i * 3, 0, 241, 112
    if kind == 'portfolio':
        icon = glyph('globe', x + 25, y + 52, 22, '#10131c', 2.3)
    else:
        icon = logo({'email': 'gmail'}.get(kind, kind), x + 25, y + 52, 22)
    cursor = f'<tspan class="cursor" fill="{TEXT}">▌</tspan>' if len(handle) < 21 else ''
    style = BLINK + f'''
.pop {{ animation: pop 6s ease-in-out infinite; animation-delay: {-delay}s; }}
@keyframes pop {{ 0%, 8%, 100% {{ transform: translateY(0); }} 4% {{ transform: translateY(-4px); }} }}
.go {{ animation: go 2.4s ease-in-out infinite; animation-delay: {-delay}s; }}
@keyframes go {{ 50% {{ transform: translate(2px, -2px); }} }}
'''
    body = f'''{window(w, h, '', 'b', bar=28, x=x, y=y, rx=12, depth=6)}
<text x="{x + w / 2}" y="{y + 18.5}" font-family="{MONO}" font-size="11" font-weight="600" fill="{TEXT_DIM}" text-anchor="middle">~/{esc(name)}</text>
<g transform="translate({x + w - 18} {y + 14})"><g class="go"><path d="{ARROW}" fill="none" stroke="{col[1]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></g></g>
<g class="pop">{raised(x + 16, y + 43, 40, 40, 10, col[1], col[2], 4, col[0])}{icon}</g>
<text x="{x + 70}" y="{y + 56}" font-family="{MONO}" font-size="11.5" font-weight="700"><tspan fill="{GREEN[1]}">$</tspan><tspan fill="{TEXT_DIM}"> {verb}</tspan></text>
<text x="{x + 70}" y="{y + 77}" font-family="{MONO}" font-size="17" font-weight="800" fill="{TEXT}">{esc(name)}</text>
<text x="{x + 70 if len(handle) < 21 else x + 16}" y="{y + 100}" font-family="{MONO}" font-size="11" fill="{col[1]}">{esc(handle)}{cursor}</text>'''
    return svg(W, H, f'{name.capitalize()}: {handle}', body, style)


# ─────────────────────────────── about ───────────────────────────────

def about():
    """About me as four separate facts, like the keys of a YAML file, each with a floating 3D key-cap
    icon: what I work on, what I studied, what I use day to day and what I'm building on the side."""
    W, H = 1000, 388
    facts = [
        (GREEN, 'server', 'working_on:', ['Backends, Automation', '& Infrastructure'], '# devops & software engineer'),
        (PURPLE, 'book-marked', 'studied:', ['Degree in', 'Software Engineering'], '# based in Sri Lanka'),
        (BLUE, 'workflow', 'day_to_day:', ['Azure, Terraform', '& CI/CD'], '# migrations & monitoring'),
        (CYAN, 'bot', 'also_building:', ['Tools For', 'AI Agents'], '# secrets & telegram, kept safe'),
    ]

    def keycap(kind, col):
        # An isometric key cap with a line icon printed on its top.
        iso = Iso(0, -18)
        return (iso.box(-28, -28, 0, 56, 56, 18, col)
                + f'<g transform="{iso.top_face(-28, -28, 18)}">' + glyph(kind, 10, 10, 36, '#10131c', 2.3) + '</g>')

    step = W / len(facts)
    xs = [step * (i + .5) for i in range(len(facts))]
    oy, floor = 200, 232

    nodes = []
    for i, (col, kind, tag, lines, sub) in enumerate(facts):
        cx = xs[i]
        shadow = f'<ellipse class="shd o{i}" cx="{cx:.0f}" cy="{floor}" rx="40" ry="8" fill="#000" opacity=".45"/>'
        tg, _ = badge(tag, col, cx, 256, 'middle', 12)
        text = ''.join(f'<text x="{cx:.0f}" y="{304 + j * 22}" font-family="{MONO}" font-size="16" font-weight="800" fill="{TEXT}" text-anchor="middle">{esc(t)}</text>'
                       for j, t in enumerate(lines))
        nodes.append(f'''<g>
  {shadow}
  <g transform="translate({cx:.0f} {oy})"><g class="obj o{i}">{keycap(kind, col)}</g></g>
  {tg}
  {text}
  <text x="{cx:.0f}" y="{304 + len(lines) * 22 + 2}" font-family="{MONO}" font-size="11.5" fill="{TEXT_DIM}" text-anchor="middle">{esc(sub)}</text>
</g>''')

    style = BLINK + '''
.obj { animation: lift 4.5s ease-in-out infinite; }
.o1 { animation-delay: -1.1s; } .o2 { animation-delay: -2.2s; } .o3 { animation-delay: -3.3s; }
@keyframes lift { 50% { transform: translate(0, -6px); } }
.shd { animation: shd 4.5s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }
@keyframes shd { 50% { transform: scale(.85); opacity: .3; } }
'''
    body = f'''<defs>{shadow_filter('soft', 10, 12, 0.45)}</defs>
{window(W, H, '~/about.md', 'a', glow=(GREEN[2], .5, 0, .6))}
{command('cat about.md', W / 2, 98, 26)}
<g filter="url(#soft)">{''.join(nodes)}</g>'''
    return svg(W, H + PAD + 8, 'About me. DevOps and software engineer working on backends, automation and infrastructure. Studied for a degree in Software Engineering; based in Sri Lanka. Day to day: Azure, Terraform and CI/CD, migrations and monitoring. Also building tools that let AI agents work safely, with secrets and Telegram.', body, style)


# ─────────────────────────────── featured projects ───────────────────────────────

PROJECTS = [
    # icon, name, repo path, (status, colour), kind, description (two lines), tech
    ('kv', 'LLM Key Vault', 'DFanso/key-vault-for-llm', ('author', PURPLE), 'secrets broker',
     ['A local secrets broker for AI coding agents: they use', 'your API keys, tokens and DB passwords unseen.'],
     ['rust', 'mcp', 'postgres', 'redis']),
    ('telegram-mcp', 'Telegram MCP', 'iddhi-sulakshana/telegram-mcp', ('contributor', CYAN), 'mcp server',
     ['Telegram for Claude Code through one always-on', 'daemon shared by every session; sends what you allow.'],
     ['typescript', 'bun', 'mcp']),
    ('server-dash', 'Server Dash', 'DFanso/server-dash', ('author', GREEN), 'self-hosted dashboard',
     ['A self-hosted dashboard for a V2rayA hotspot: CPU,', 'memory, throughput and status, as one binary.'],
     ['rust', 'react', 'typescript']),
    ('bridge-relay', 'Bridge Relay', 'DFanso/bridge-relay', ('author', AMBER), 'claude code · ssh relay',
     ['Joins Claude Code session-bridge across machines', 'over SSH: a remote session shows up as a local peer.'],
     ['python', 'ssh', 'claude-code']),
]


def app_icon(key, s):
    """A project's own icon (icons/projects/) as a raised app tile, s×s at the origin."""
    r = round(s * .26, 1)
    tile = f'<rect width="{s}" height="{s}" rx="{r}"'
    out = f'<rect y="5" width="{s}" height="{s}" rx="{r}" fill="{LIP}"/><clipPath id="ic-{key}">{tile}/></clipPath><g clip-path="url(#ic-{key})">'
    if key == 'bridge-relay':
        # No icon of its own: a cable glyph on a tile in the card's colour.
        out += (f'<linearGradient id="br" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{AMBER[0]}"/><stop offset="1" stop-color="{AMBER[2]}"/></linearGradient>'
                f'{tile} fill="url(#br)"/>' + glyph('cable', s * .22, s * .22, s * .56, '#10131c', 2.2))
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
    out += (f'</g><rect width="{s}" height="{s / 2:.0f}" rx="{r}" fill="#fff" opacity=".06"/>'
            f'<rect x=".75" y=".75" width="{s - 1.5}" height="{s - 1.5}" rx="{r - .75}" fill="none" stroke="#fff" stroke-opacity=".14" stroke-width="1.5"/>')
    return out


def projects_title():
    """The projects heading on its own, so each project card below it can be a link."""
    W = 1000
    p, h = plate('ls ~/projects', W / 2)
    return svg(W, h + 6 + PAD, 'Featured projects', p, BLINK)


def project_card(i):
    """One featured project as an editor window. The README shows two side by side, each half of
    NARROW wide; card i%2 sits 6px in, so a pair fills the row edge to edge with a 12px gap."""
    key, name, repo, (status, col), kind, desc, tech = PROJECTS[i]
    W, w, h = 500, 494, 228
    H = h + 8 + PAD
    x = (i % 2) * 6
    delay = i * .5
    chips, cx = [], x + 22
    for t in tech:
        tw = round(18 + len(t) * 7.2)
        chips.append(f'<rect x="{cx}" y="192" width="{tw}" height="22" rx="6" fill="{LIP}"/>'
                     f'<rect x="{cx}" y="189" width="{tw}" height="22" rx="6" fill="{CARD_TOP}" stroke="{EDGE}" stroke-width="1.2"/>'
                     f'<text x="{cx + tw / 2:.1f}" y="204" font-family="{MONO}" font-size="12" font-weight="700" fill="{TEXT_SOFT}" text-anchor="middle">{esc(t)}</text>')
        cx += tw + 8
    lines = ''.join(f'<text x="{x + 22}" y="{152 + j * 19}" font-family="{MONO}" font-size="12.4" fill="{TEXT_SOFT}">{esc(t)}</text>'
                    for j, t in enumerate(desc))
    bdg, _ = badge(f'[{status}]', col, x + 102, 50)
    style = f'''
.bob {{ animation: bob 4.5s ease-in-out infinite; animation-delay: {-delay}s; }}
@keyframes bob {{ 50% {{ transform: translateY(-4px); }} }}
.go {{ animation: go 2.4s ease-in-out infinite; animation-delay: {-delay}s; }}
@keyframes go {{ 50% {{ transform: translate(2px, -2px); }} }}
'''
    body = f'''{window(w, h, f'~/projects/{repo.split("/")[1]}', 'p', bar=34, x=x, rx=14, depth=7)}
<g transform="translate({x + w - 22} 17)"><g class="go"><path d="{ARROW}" fill="none" stroke="{col[1]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></g></g>
<g transform="translate({x + 22} 52)"><g class="bob">{app_icon(key, 62)}</g></g>
{bdg}
<text x="{x + 102}" y="100" font-family="{MONO}" font-size="22" font-weight="800" fill="{TEXT}">{esc(name)}</text>
<text x="{x + 102}" y="120" font-family="{MONO}" font-size="12" fill="{TEXT_DIM}"># {esc(kind)} · {esc(repo.split('/')[0])}</text>
{lines}
{''.join(chips)}'''
    label = f'{name} ({status}): {kind}. {" ".join(desc)} Built with {", ".join(tech)}.'
    return svg(W, H, label, body, style)


# ─────────────────────────────── stack ───────────────────────────────

GROUPS = [
    ('cloud-and-deploy/', CYAN, [('AWS', 'aws'), ('Azure', 'azure'), ('Cloudflare', 'cloudflare'), ('Docker', 'docker'),
                                 ('Kubernetes', 'kubernetes'), ('K3s', 'k3s'), ('Dokploy', 'dokploy')]),
    ('backend-and-data/', AMBER, [('NestJS', 'nestjs'), ('Node.js', 'nodejs'), ('Go', 'go'), ('Python', 'python'), ('Rust', 'rust'),
                                  ('C# / .NET', 'csharp'), ('PostgreSQL', 'postgresql'), ('MongoDB', 'mongodb'), ('Redis', 'redis')]),
    ('frontend/', RED, [('React', 'react'), ('Next.js', 'nextjs'), ('Astro', 'astro'), ('Tailwind', 'tailwind')]),
    ('devops-and-iac/', GREEN, [('Terraform', 'terraform'), ('GH Actions', 'github-actions'), ('Jenkins', 'jenkins'), ('ArgoCD', 'argocd'),
                                ('Prometheus', 'prometheus'), ('Grafana', 'grafana'), ('Sentry', 'sentry')]),
    ('ai-and-workflow/', PURPLE, [('Claude', 'claude'), ('Git', 'git'), ('GitHub', 'github'), ('ClickUp', 'clickup')]),
]
PER_ROW = 9


def stack():
    """The toolbox as a directory listing: each group a folder, each tool a raised key in it
    (no window), PER_ROW to a row; a group with more tools than that wraps onto another row."""
    W, gap, sh = 1000, 14, 100
    sw = (W - (PER_ROW - 1) * gap) / PER_ROW
    head, hh = plate('ls ~/stack', W / 2)
    out, y, n = [], hh + 40, 0
    for name_, col, tools in GROUPS:
        _, cw = chip_label(name_, col, 0, 0)
        chip, _ = chip_label(name_, col, round((W - cw) / 2), y)
        rule = f'stroke="{EDGE}" stroke-width="1.5" stroke-dasharray="6 6"'
        out.append(chip + f'<path d="M0 {y + 13} H{(W - cw) / 2 - 14:.0f} M{(W + cw) / 2 + 14:.0f} {y + 13} H{W}" {rule}/>')
        y += 46
        for i, (name, key) in enumerate(tools):
            if i and i % PER_ROW == 0:
                y += sh + 6 + gap
            left = len(tools) - i + i % PER_ROW
            row_n = min(PER_ROW, left)
            x = (W - (row_n * sw + (row_n - 1) * gap)) / 2 + (i % PER_ROW) * (sw + gap)
            out.append(f'''<g transform="translate({x:.1f} {y})">
  {raised(0, 0, round(sw, 1), sh, 12, CARD, LIP, 6, EDGE)}
  <rect x="8" y="8" width="{sw - 16:.1f}" height="60" rx="8" fill="{SLOT}"/>
  <rect x="8" y="8" width="{sw - 16:.1f}" height="2" rx="1" fill="{col[1]}" opacity=".55"/>
  <ellipse cx="{sw / 2:.1f}" cy="60" rx="18" ry="3.5" fill="#000" opacity=".5"/>
  <g class="item" style="animation-delay:{-n * .37:.2f}s">{logo(key, round(sw / 2 - 17, 1), 21, 34)}</g>
  <text x="{sw / 2:.1f}" y="88" font-family="{MONO}" font-size="11.5" font-weight="700" fill="{TEXT}" text-anchor="middle">{esc(name)}</text>
</g>''')
            n += 1
        y += sh + 6 + 30
    H = y - 30 + PAD
    style = BLINK + '''
.item { animation: hover 3.6s ease-in-out infinite; }
@keyframes hover { 50% { transform: translateY(-3px); } }
'''
    body = f'''<defs>{shadow_filter('soft', 6, 6, 0.35)}</defs>
<g filter="url(#soft)">{head}{''.join(out)}</g>'''
    names = ', '.join(name for _, _, tools in GROUPS for name, _ in tools)
    return svg(W, H, f'My toolbox: {names}', body, style)


# ─────────────────────────────── divider & footer ───────────────────────────────

def divider():
    """A dashed rule as wide as the blocks around it (they're shown at NARROW of the README's
    width), centred between them, with a small `$` marker in the middle."""
    W = 1000
    pad = round(PAD * NARROW)
    H = 10 + 10 + pad
    x0 = W * (1 - NARROW) / 2
    rule = f'stroke="{BLUE[2]}" stroke-opacity=".6" stroke-width="2" stroke-dasharray="8 6"'
    body = (f'<path d="M{x0:g} 10 H{W / 2 - 24:g} M{W / 2 + 24:g} 10 H{W - x0:g}" {rule}/>'
            f'<text x="{W / 2:g}" y="15" font-family="{MONO}" font-size="14" font-weight="800" fill="{GREEN[1]}" fill-opacity=".8" text-anchor="middle">$_</text>')
    return svg(W, H, '', body)


def footer():
    """A closing terminal session, with a server rack on the left and a container stack on the right."""
    W, H = 1000, 280
    liso = Iso(150, 150)
    left = rack(liso, -36, -24, 0, 4, 72, 48, 17)
    lx, ly = liso.p(0, 0, 0)
    riso = Iso(850, 150)
    right = (container(riso, -30, -30, 0, 32, BLUE) + container(riso, 4, -30, 0, 32, CYAN)
             + container(riso, -30, 4, 0, 32, PURPLE) + container(riso, -13, -13, 32, 32, GREEN))
    rx_, ry_ = riso.p(0, 0, 0)
    halo = (f'<ellipse class="halo" cx="{lx:.0f}" cy="{ly - 20:.0f}" rx="120" ry="80" fill="url(#halo)"/>'
            f'<ellipse class="halo h2" cx="{rx_:.0f}" cy="{ry_ - 20:.0f}" rx="120" ry="80" fill="url(#halo)"/>')
    cx = W / 2
    style = BLINK + '''
.lift { animation: lift 5s ease-in-out infinite; }
.l2 { animation-delay: -2.5s; }
@keyframes lift { 50% { transform: translateY(-5px); } }
.blink { animation: blink 2.4s steps(1) infinite; }
@keyframes blink { 50% { opacity: .3; } }
.halo { animation: halo 4s ease-in-out infinite; }
.h2 { animation-delay: -2s; }
@keyframes halo { 50% { opacity: .5; } }
'''
    body = f'''<defs>{shadow_filter('soft', 12, 12, 0.55)}
<radialGradient id="halo"><stop offset="0" stop-color="{GREEN[1]}" stop-opacity=".16"/><stop offset="1" stop-color="{GREEN[1]}" stop-opacity="0"/></radialGradient></defs>
{window(W, H, 'leo@dfanso: ~ — exit', 'f', glow=(GREEN[2], .5, .55, .6))}
{halo}
<g filter="url(#soft)"><g class="lift">{left}</g><g class="lift l2">{right}</g></g>
<text x="{cx + 10}" y="80" font-family="{MONO}" font-size="13" font-weight="800" fill="{GREEN[1]}" text-anchor="middle">all checks passed <tspan fill="{TEXT_DIM}">[ok]</tspan></text>
<path d="M{cx - 96} 75 l4 4 l8 -9" fill="none" stroke="{GREEN[1]}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
{command('echo "thanks for stopping by!"', cx, 124, 25, cursor=False)}
<text x="{cx}" y="160" font-family="{MONO}" font-size="15" font-weight="600" fill="{TEXT_SOFT}" text-anchor="middle"># visit my site to see what I'm building lately</text>
<text x="{cx}" y="196" font-family="{MONO}" font-size="15" font-weight="700" text-anchor="middle"><tspan fill="{GREEN[1]}">$</tspan><tspan fill="{TEXT}"> open </tspan><tspan fill="{CYAN[1]}">https://itsme.dfanso.dev</tspan><tspan class="cursor" fill="{TEXT}"> ▌</tspan></text>
<text x="{cx}" y="236" font-family="{MONO}" font-size="12" fill="{TEXT_DIM}" text-anchor="middle">logout · exit 0</text>
<text x="{lx:.0f}" y="252" font-family="{MONO}" font-size="12" font-weight="800" fill="{GREEN[1]}" text-anchor="middle">[deploy]</text>
<text x="{rx_:.0f}" y="252" font-family="{MONO}" font-size="12" font-weight="800" fill="{TEXT_DIM}" text-anchor="middle">[rollback?]</text>'''
    return svg(W, H + PAD + 8, "Thanks for stopping by! Visit my website to see what I'm building lately.", body, style)


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
