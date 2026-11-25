"""Draws the live GitHub stat cards in the README's dark arcade theme (see
theme.py): the headline stats (lifetime and this year's contributions, PRs and
so on, private repos included when the token can see them), the contribution
streak and top languages. Run by
.github/workflows/profile-assets.yml, which publishes them to the `output` branch.

Usage: GITHUB_TOKEN=... python stat_cards.py <github-user> <out-dir>
"""
import datetime as dt
import json
import os
import re
import sys
import urllib.request
from collections import Counter

from theme import (BUTTER, CARD_TOP, LILAC, LIP, MONO, PAD, PEACH, ROSE, SAGE, SANS, SKY, TEXT, TEXT_DIM, TEXT_SOFT, TWINKLE,
                   esc, glyph, header_center, panel, raised, shadow_filter, stars, svg)

INK = '#2e2a36'


# ───────────────────────────── data ─────────────────────────────

def get(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers={'User-Agent': 'profile-stat-cards', **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode('utf-8')


def gql(query, **variables):
    body = json.dumps({'query': query, 'variables': variables}).encode()
    res = json.loads(get('https://api.github.com/graphql', body, {'Authorization': f"Bearer {os.environ['GITHUB_TOKEN']}"}))
    if res.get('errors'):
        raise RuntimeError(res['errors'])
    return res['data']


USER_QUERY = '''query($login: String!) { user(login: $login) {
  createdAt
  followers { totalCount }
  pullRequests { totalCount }
  issues { totalCount }
  repositoriesContributedTo(contributionTypes: [COMMIT, ISSUE, PULL_REQUEST, REPOSITORY]) { totalCount }
  allRepos: repositories(ownerAffiliations: OWNER) { totalCount }
  repositories(first: 100, ownerAffiliations: OWNER, isFork: false) { nodes {
    stargazerCount
    primaryLanguage { name color }
    languages(first: 10, orderBy: { field: SIZE, direction: DESC }) { edges { size node { name color } } }
  } }
  contributionsCollection { contributionYears }
} }'''

YEAR_QUERY = '''query($login: String!, $from: DateTime!, $to: DateTime!) { user(login: $login) {
  contributionsCollection(from: $from, to: $to) {
    contributionCalendar { weeks { contributionDays { date contributionCount } } }
  }
} }'''


def profile_views(user):
    # komarev only counts requests from GitHub's image proxy, so reading it here doesn't add a view.
    try:
        nums = re.findall(r'>([\d,]+)<', get(f'https://komarev.com/ghpvc/?username={user}'))
        return int(nums[-1].replace(',', '')) if nums else None
    except Exception as e:
        print(f'::warning::profile views: {e}')
        return None


def collect(login):
    u = gql(USER_QUERY, login=login)['user']
    days = {}
    for year in u['contributionsCollection']['contributionYears']:
        c = gql(YEAR_QUERY, login=login, **{'from': f'{year}-01-01T00:00:00Z', 'to': f'{year}-12-31T23:59:59Z'})
        cc = c['user']['contributionsCollection']
        for week in cc['contributionCalendar']['weeks']:
            for d in week['contributionDays']:
                days[dt.date.fromisoformat(d['date'])] = d['contributionCount']

    today = dt.datetime.now(dt.timezone.utc).date()
    days = {d: n for d, n in days.items() if d <= today}
    order = sorted(days)

    # Streaks. Today doesn't break the current streak until it's over.
    longest, run, run_start, best = 0, 0, None, (None, None)
    for d in order:
        if days[d]:
            run_start = d if run == 0 else run_start
            run += 1
            if run > longest:
                longest, best = run, (run_start, d)
        else:
            run = 0
    current, cur_end = 0, today if days.get(today) else today - dt.timedelta(days=1)
    d = cur_end
    while days.get(d):
        current += 1
        d -= dt.timedelta(days=1)
    cur_start = d + dt.timedelta(days=1)

    langs, lang_color, repos_per_lang, stars_ = Counter(), {}, Counter(), 0
    for r in u['repositories']['nodes']:
        stars_ += r['stargazerCount']
        if r['primaryLanguage']:
            repos_per_lang[r['primaryLanguage']['name']] += 1
        for e in r['languages']['edges']:
            langs[e['node']['name']] += e['size']
            lang_color[e['node']['name']] = e['node']['color'] or '#8b8b9e'

    return {
        'joined': dt.date.fromisoformat(u['createdAt'][:10]),
        'today': today,
        'total': sum(days.values()),
        'year': sum(n for d, n in days.items() if d.year == today.year),
        'prs': u['pullRequests']['totalCount'],
        'issues': u['issues']['totalCount'],
        'contributed': u['repositoriesContributedTo']['totalCount'],
        'followers': u['followers']['totalCount'],
        'repos': u['allRepos']['totalCount'],
        'stars': stars_,
        'views': profile_views(login),
        'current': current, 'current_range': (cur_start, cur_end) if current else None,
        'longest': longest, 'longest_range': best,
        'langs': [(name, size, lang_color[name]) for name, size in langs.most_common()],
        'repos_per_lang': repos_per_lang,
    }


# ───────────────────────────── helpers ─────────────────────────────

def fmt(n):
    if n is None:
        return '—'
    if n >= 1_000_000:
        return f'{n / 1_000_000:.1f}M'.replace('.0M', 'M')
    if n >= 10_000:
        return f'{n / 1000:.1f}k'.replace('.0k', 'k')
    return f'{n:,}'


def day(d):
    return f'{d:%b} {d.day}, {d.year}' if d else ''


def span(r):
    if not r or not r[0]:
        return 'start one today'
    a, b = r
    if a == b:
        return day(a)
    return f'{a:%b} {a.day} – {b:%b} {b.day}, {b.year}' if a.year == b.year else f'{day(a)} – {day(b)}'


_bars = [0]


def bar(x, y, w, h, pct, color, cls='fill', delay=0):
    """A sunken track with a clay fill; a glint runs along the fill now and then."""
    fw = max(w * min(pct, 1), h if pct > 0 else 0)
    track = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}" fill="{LIP}"/>'
    if not fw:
        return track
    _bars[0] += 1
    cid = f'bar{_bars[0]}'
    return (track
            + f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{fw:.1f}" height="{h}" rx="{h / 2}"/></clipPath>'
            f'<g clip-path="url(#{cid})"><rect x="{x}" y="{y}" width="{fw:.1f}" height="{h}" fill="{color}"/>'
            f'<rect x="{x}" y="{y + h * .15:.1f}" width="{fw:.1f}" height="{h * .3:.1f}" fill="#fff" opacity=".3"/>'
            f'<rect class="{cls}" style="animation-delay:{delay}s" x="{x - 30}" y="{y - 2}" width="18" height="{h + 4}" fill="#fff" opacity=".45"/></g>')


GROW = '''
.fill { animation: glint 4s ease-in-out infinite; }
@keyframes glint { 0% { transform: translateX(0); } 45%, 100% { transform: translateX(400px); } }
'''


# ───────────────────────────── cards ─────────────────────────────

def player(s):
    """The headline numbers as loose clay tiles (no panel), to sit right under the hero."""
    # Flush with the panels (x 0..1000).
    W, H = 1000, 92 + 12 + 92 + 6 + PAD
    tiles = [
        ('git-pull-request', LILAC, s['prs'], 'Pull requests'),
        ('bug', ROSE, s['issues'], 'Issues'),
        ('folder-git-2', SKY, s['contributed'], 'Contributed to'),
        ('star', BUTTER, s['stars'], 'Stars earned'),
        ('book-marked', PEACH, s['repos'], 'Repositories'),
        ('users', SAGE, s['followers'], 'Followers'),
        ('eye', SKY, s['views'], 'Profile views'),
        ('calendar-days', PEACH, s['year'], f"{s['today'].year} so far"),
    ]
    tw, th, gap, tx0 = 164, 92, 12, 308
    out = []
    for i, (icon, col, value, label) in enumerate(tiles):
        x, y = tx0 + (i % 4) * (tw + gap), (i // 4) * (th + gap)
        out.append(f'''<g transform="translate({x} {y})">{raised(0, 0, tw, th, 18)}
  <g class="pop" style="animation-delay:{-i * .4:.1f}s"><circle cx="30" cy="30" r="16" fill="{col[1]}"/><circle cx="30" cy="27" r="16" fill="{col[0]}"/>{glyph(icon, 21, 18, 18, INK, 2.4)}</g>
  <text x="56" y="32" font-family="{SANS}" font-size="12.5" font-weight="700" fill="{TEXT_SOFT}">{esc(label)}</text>
  <text x="18" y="77" font-family="{SANS}" font-size="26" font-weight="800" fill="{TEXT}">{fmt(value)}</text>
</g>''')

    big = f'''<g>{raised(0, 0, 296, 196, 24)}
  <g class="bob"><circle cx="48" cy="52" r="26" fill="{BUTTER[2]}"/><circle cx="48" cy="47" r="26" fill="{BUTTER[0]}"/>
  <circle cx="48" cy="47" r="20" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="1.5"/>{glyph('flame', 35, 34, 26, INK, 2.3)}</g>
  <text x="90" y="44" font-family="{MONO}" font-size="11.5" font-weight="800" letter-spacing=".5" fill="{BUTTER[1]}">Lifetime</text>
  <text x="90" y="62" font-family="{MONO}" font-size="11.5" font-weight="800" letter-spacing=".5" fill="{BUTTER[1]}">Contributions</text>
  <text x="24" y="138" font-family="{SANS}" font-size="52" font-weight="900" fill="{TEXT}">{fmt(s['total'])}</text>
  <text x="24" y="170" font-family="{SANS}" font-size="13" fill="{TEXT_SOFT}">since {s['joined']:%b %Y} · private repos included</text>
</g>'''
    style = '''
.bob { animation: bob 4s ease-in-out infinite; }
@keyframes bob { 50% { transform: translateY(-4px); } }
.pop { animation: pop 6s ease-in-out infinite; }
@keyframes pop { 0%, 8%, 100% { transform: translateY(0); } 4% { transform: translateY(-4px); } }
'''
    body = f'''<defs>{shadow_filter('soft', 6, 6, 0.35)}</defs>
<g filter="url(#soft)">{big}{''.join(out)}</g>'''
    label = (f"{s['total']:,} lifetime contributions, {s['year']:,} this year. Pull requests {s['prs']:,}, issues {s['issues']:,}, "
             f"contributed to {s['contributed']} repos, {s['stars']} stars, {s['repos']} repositories, {s['followers']} followers, {fmt(s['views'])} profile views.")
    return svg(W, H, label, body, style)


PANEL_H = 330


def streak(s):
    W, H = 494, PANEL_H
    cx, cy = W / 2, 208

    def column(x, value, label, sub, col):
        return (f'<text x="{x}" y="{cy - 4}" font-family="{SANS}" font-size="28" font-weight="800" fill="{TEXT}" text-anchor="middle">{value}</text>'
                f'<text x="{x}" y="{cy + 22}" font-family="{SANS}" font-size="13" font-weight="700" fill="{col}" text-anchor="middle">{label}</text>'
                f'<text x="{x}" y="{cy + 42}" font-family="{SANS}" font-size="11" fill="{TEXT_DIM}" text-anchor="middle">{esc(sub)}</text>')

    ring = f'''<g transform="translate({cx} {cy})">
  <circle r="52" fill="{LIP}"/>
  <circle r="46" fill="none" stroke="url(#ringg)" stroke-width="9" stroke-dasharray="230 60" stroke-linecap="round" transform="rotate(-53)"/>
  <circle r="36" fill="{CARD_TOP}"/>
  <text y="12" font-family="{SANS}" font-size="32" font-weight="900" fill="{TEXT}" text-anchor="middle">{s['current']}</text>
  <g transform="translate(-17 -84)">
    <path d="M17 2c3 7 13 11 13 23a13 13 0 0 1-26 0c0-6 3-10 6-13 0 5 3 7 5 7-1-6 0-12 2-17Z" fill="{PEACH[2]}"/>
    <path d="M17 14c2 5 7 7 7 13a7 7 0 0 1-14 0c0-3 2-5 3-6 1 3 2 4 3 4 0-4 0-7 1-11Z" fill="{BUTTER[0]}"/>
  </g>
</g>'''
    # The ring holds still, its gap turned to the top under the flame; only a soft warm glow breathes behind it.
    glow = f'<circle class="breathe" cx="{cx}" cy="{cy}" r="62" fill="{PEACH[2]}" filter="url(#warm)"/>'
    body = f'''<defs>{shadow_filter('soft', 8, 8, 0.45)}
<filter id="warm" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="14"/></filter>
<linearGradient id="ringg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BUTTER[1]}"/><stop offset="1" stop-color="{PEACH[2]}"/></linearGradient></defs>
{panel(W, H, (PEACH[2], .5, .6, .5), 'st')}
{stars(W, H, 14, 3)}
{header_center('My Streak', 'Combo', PEACH, cx, 30, 'Days In A Row', 26)}
{column(84, fmt(s['total']), 'Contributions', f"since {s['joined']:%b} {s['joined'].year}", SKY[1])}
{column(W - 84, s['longest'], 'Best combo', span(s['longest_range']), LILAC[1])}
{glow}
<g filter="url(#soft)">{ring}</g>
<text x="{cx}" y="{cy + 78}" font-family="{SANS}" font-size="13" font-weight="700" fill="{PEACH[1]}" text-anchor="middle">Current streak</text>
<text x="{cx}" y="{cy + 96}" font-family="{SANS}" font-size="11" fill="{TEXT_DIM}" text-anchor="middle">{esc(span(s['current_range']))}</text>'''
    style = TWINKLE + '''
.breathe { opacity: .18; animation: breathe 3.6s ease-in-out infinite; }
@keyframes breathe { 50% { opacity: .5; } }
'''
    label = f"Contribution streak: {s['current']} days now, best {s['longest']} days, {s['total']:,} contributions in total."
    return body, style, label


def languages(s):
    W, H = 494, PANEL_H
    top = s['langs'][:6]
    total = sum(size for _, size, _ in s['langs']) or 1
    rows = []
    # 36px clear on both sides: dot and name, bar, percentage, repo count.
    for i, (name, size, color) in enumerate(top):
        y = 136 + i * 30
        n = s['repos_per_lang'].get(name, 0)
        rows.append(f'<circle cx="41" cy="{y + 6}" r="5" fill="{color}"/>'
                    f'<text x="54" y="{y + 11}" font-family="{SANS}" font-size="13.5" font-weight="700" fill="{TEXT}">{esc(name)}</text>'
                    f'{bar(156, y, 172, 12, size / total, color, "fill", i * .12)}'
                    f'<text x="390" y="{y + 11}" font-family="{MONO}" font-size="12" font-weight="700" fill="{TEXT_SOFT}" text-anchor="end">{size / total * 100:.1f}%</text>'
                    f'<text x="{W - 36}" y="{y + 11}" font-family="{MONO}" font-size="11" fill="{TEXT_DIM}" text-anchor="end">{f"{n} repo" + ("s" if n > 1 else "") if n else "·"}</text>')
    body = f'''{panel(W, H, (SKY[2], .9, .1, .6), 'lg')}
{header_center('Top Languages', 'Skill Tree', SKY, W / 2, 30, 'By Code Size · Private Repos Too', 26)}
{''.join(rows)}'''
    label = 'Top languages: ' + ', '.join(f'{n} {sz / total * 100:.0f}%' for n, sz, _ in top)
    return body, GROW, label


def streak_and_languages(s):
    """The streak and top languages panels side by side in one image, with the same 12px gap as the tiles."""
    b1, s1, l1 = streak(s)
    b2, s2, l2 = languages(s)
    body = f'<g>{b1}</g>\n<g transform="translate(506 0)">{b2}</g>'
    return svg(1000, PANEL_H + PAD, f'{l1} {l2}', body, s1 + s2)


def main():
    login, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    s = collect(login)
    cards = {
        'stats-player.svg': player(s),
        'stats-streak-languages.svg': streak_and_languages(s),
    }
    for name, text in cards.items():
        with open(os.path.join(out, name), 'w', encoding='utf-8', newline='\n') as f:
            f.write(text)
    print({k: v for k, v in s.items() if k not in ('months', 'langs')})


if __name__ == '__main__':
    main()
