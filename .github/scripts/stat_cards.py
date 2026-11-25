"""Draws the live GitHub stat cards in the README's dark terminal theme (see
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

from theme import (AMBER, BLUE, CARD, CYAN, DEPTH, EDGE, GREEN, LIP, MONO, PAD, PURPLE, RED, SLOT, TEXT, TEXT_DIM,
                   TEXT_SOFT, command, esc, glyph, raised, svg, window)

SPARK_DAYS = 60


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
        # The last SPARK_DAYS days, oldest first, for the streak card's sparkline.
        'recent': [days.get(today - dt.timedelta(days=k), 0) for k in range(SPARK_DAYS - 1, -1, -1)],
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


# ───────────────────────────── cards ─────────────────────────────

def player(s):
    """The headline numbers as a neofetch-style window: one big raised card for lifetime
    contributions, then key: value tiles."""
    W, H = 1000, 252
    tiles = [
        ('git-pull-request', PURPLE, s['prs'], 'pull_requests'),
        ('bug', RED, s['issues'], 'issues'),
        ('folder-git-2', CYAN, s['contributed'], 'contributed_to'),
        ('star', AMBER, s['stars'], 'stars'),
        ('book-marked', BLUE, s['repos'], 'repositories'),
        ('users', GREEN, s['followers'], 'followers'),
        ('eye', CYAN, s['views'], 'profile_views'),
        ('calendar-days', AMBER, s['year'], f"commits_{s['today'].year}"),
    ]
    tw, th, gap, tx0, ty0 = 155, 80, 12, 320, 60
    out = []
    for i, (icon, col, value, label) in enumerate(tiles):
        x, y = tx0 + (i % 4) * (tw + gap), ty0 + (i // 4) * (th + gap)
        out.append(f'''<g transform="translate({x} {y})">{raised(0, 0, tw, th, 10, CARD, LIP, 5, EDGE)}
  <rect x="0" y="12" width="3" height="20" rx="1.5" fill="{col[1]}"/>
  {glyph(icon, 14, 14, 15, col[1], 2.2)}
  <text x="36" y="26" font-family="{MONO}" font-size="11.5" font-weight="700" fill="{TEXT_DIM}">{esc(label)}<tspan fill="{TEXT_DIM}">:</tspan></text>
  <text x="14" y="64" font-family="{MONO}" font-size="25" font-weight="800" fill="{TEXT}">{fmt(value)}</text>
</g>''')

    big = f'''<g transform="translate(24 {ty0})">{raised(0, 0, 284, 2 * th + gap, 12, CARD, LIP, 5, EDGE)}
  <text x="20" y="32" font-family="{MONO}" font-size="12.5" font-weight="700"><tspan fill="{GREEN[1]}">$</tspan><tspan fill="{TEXT_SOFT}"> stats --lifetime</tspan></text>
  <text x="20" y="54" font-family="{MONO}" font-size="11.5" fill="{TEXT_DIM}"># lifetime contributions</text>
  <text x="20" y="116" font-family="{MONO}" font-size="48" font-weight="800" fill="{GREEN[0]}">{fmt(s['total'])}</text>
  <text x="20" y="150" font-family="{MONO}" font-size="11.5" fill="{TEXT_DIM}">since {s['joined']:%b %Y} · private repos incl.</text>
</g>'''
    body = f'''{window(W, H - DEPTH, 'leo@dfanso: ~ — neofetch', 'np', glow=(GREEN[2], .1, .4, .5))}
{big}{''.join(out)}'''
    label = (f"{s['total']:,} lifetime contributions, {s['year']:,} this year. Pull requests {s['prs']:,}, issues {s['issues']:,}, "
             f"contributed to {s['contributed']} repos, {s['stars']} stars, {s['repos']} repositories, {s['followers']} followers, {fmt(s['views'])} profile views.")
    return svg(W, H + PAD, label, body)


PANEL_H = 330


def sparkline(s, x, y, w, h):
    """The last SPARK_DAYS days as little raised columns, the current streak lit green."""
    days = s['recent']
    n = len(days)
    step = w / n
    bw = step * .62
    top = max(days) or 1
    streak_from = n - s['current'] if s['current'] else n
    if s['current'] and not days[-1]:
        streak_from -= 1  # today hasn't started; the streak ended yesterday
    out = [f'<rect x="{x - 8}" y="{y - 8}" width="{w + 16}" height="{h + 30}" rx="8" fill="{SLOT}"/>'
           f'<path d="M{x} {y + h + .5} H{x + w}" stroke="{EDGE}" stroke-width="1"/>']
    for i, v in enumerate(days):
        bx = x + i * step + (step - bw) / 2
        if not v:
            out.append(f'<rect x="{bx:.1f}" y="{y + h - 2}" width="{bw:.1f}" height="2" rx="1" fill="{EDGE}"/>')
            continue
        bh = max(4, (h - 4) * (v / top) ** .6)
        col = GREEN if i >= streak_from else BLUE
        out.append(f'<rect x="{bx + 1.5:.1f}" y="{y + h - bh + 1.5:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="1.5" fill="{col[2]}"/>'
                   f'<rect class="col" style="animation-delay:{i * .02:.2f}s" x="{bx:.1f}" y="{y + h - bh:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="1.5" fill="{col[1]}"/>')
    out.append(f'<text x="{x}" y="{y + h + 16}" font-family="{MONO}" font-size="10.5" fill="{TEXT_DIM}">-{n}d</text>'
               f'<text x="{x + w}" y="{y + h + 16}" font-family="{MONO}" font-size="10.5" fill="{TEXT_DIM}" text-anchor="end">today</text>'
               f'<text x="{x + w / 2}" y="{y + h + 16}" font-family="{MONO}" font-size="10.5" fill="{TEXT_DIM}" text-anchor="middle">'
               f'<tspan fill="{GREEN[1]}">■</tspan> streak  <tspan fill="{BLUE[1]}">■</tspan> commits</text>')
    return ''.join(out)


def streak(s):
    W, H = 494, PANEL_H - DEPTH

    def row(y, key, value, sub, col):
        return (f'<text x="28" y="{y}" font-family="{MONO}" font-size="13" font-weight="700" fill="{TEXT_DIM}">{key}:</text>'
                f'<text x="186" y="{y}" font-family="{MONO}" font-size="15" font-weight="800" fill="{col[1]}">{esc(value)}</text>'
                f'<text x="{W - 28}" y="{y}" font-family="{MONO}" font-size="11" fill="{TEXT_DIM}" text-anchor="end">{esc(sub)}</text>')

    plural = lambda n: f"{n} day" + ("" if n == 1 else "s")
    body = f'''{window(W, H, '~/streak — git log', 'st', glow=(GREEN[2], .5, .3, .6))}
{command('git log --streak', W / 2, 84, 20)}
{row(126, 'current', plural(s['current']), span(s['current_range']), GREEN)}
{row(152, 'longest', plural(s['longest']), span(s['longest_range']), PURPLE)}
{row(178, 'total', fmt(s['total']), f"since {s['joined']:%b} {s['joined'].year}", CYAN)}
{sparkline(s, 36, 210, W - 72, 58)}'''
    style = '''
.col { animation: col 6s ease-in-out infinite; }
@keyframes col { 0%, 90%, 100% { opacity: 1; } 95% { opacity: .55; } }
'''
    label = f"Contribution streak: {s['current']} days now, best {s['longest']} days, {s['total']:,} contributions in total."
    return body, style, label


def meter(x, y, pct, color, cells=22):
    """An htop-style meter: [|||||      ] drawn as cells, at least one lit for any non-zero share."""
    lit = 0 if pct <= 0 else max(1, round(pct * cells))
    out = [f'<text x="{x}" y="{y + 11}" font-family="{MONO}" font-size="13" font-weight="700" fill="{TEXT_DIM}">[</text>']
    for k in range(cells):
        on = k < lit
        attrs = f'class="cell" style="animation-delay:{k * .05:.2f}s" fill="{color}"' if on else f'fill="{EDGE}" opacity=".6"'
        out.append(f'<rect {attrs} x="{x + 11 + k * 7}" y="{y + 1}" width="5" height="12" rx="1"/>')
    out.append(f'<text x="{x + 11 + cells * 7 + 1}" y="{y + 11}" font-family="{MONO}" font-size="13" font-weight="700" fill="{TEXT_DIM}">]</text>')
    return ''.join(out)


def languages(s):
    W, H = 494, PANEL_H - DEPTH
    top = s['langs'][:6]
    total = sum(size for _, size, _ in s['langs']) or 1
    rows = [f'<rect x="20" y="108" width="{W - 40}" height="22" rx="4" fill="{GREEN[2]}" fill-opacity=".25"/>'
            f'<text x="28" y="123" font-family="{MONO}" font-size="11" font-weight="800" fill="{GREEN[0]}">LANG</text>'
            f'<text x="142" y="123" font-family="{MONO}" font-size="11" font-weight="800" fill="{GREEN[0]}">SIZE</text>'
            f'<text x="380" y="123" font-family="{MONO}" font-size="11" font-weight="800" fill="{GREEN[0]}" text-anchor="end">%</text>'
            f'<text x="{W - 28}" y="123" font-family="{MONO}" font-size="11" font-weight="800" fill="{GREEN[0]}" text-anchor="end">REPOS</text>']
    for i, (name, size, color) in enumerate(top):
        y = 142 + i * 25
        n = s['repos_per_lang'].get(name, 0)
        rows.append(f'<circle cx="32" cy="{y + 7}" r="4" fill="{color}"/>'
                    f'<text x="42" y="{y + 11}" font-family="{MONO}" font-size="12.5" font-weight="700" fill="{TEXT}">{esc(name[:11])}</text>'
                    f'{meter(140, y, size / total, color)}'
                    f'<text x="380" y="{y + 11}" font-family="{MONO}" font-size="12" font-weight="700" fill="{TEXT_SOFT}" text-anchor="end">{size / total * 100:.1f}</text>'
                    f'<text x="{W - 28}" y="{y + 11}" font-family="{MONO}" font-size="12" fill="{TEXT_DIM}" text-anchor="end">{n if n else "-"}</text>')
    body = f'''{window(W, H, '~/langs — top', 'lg', glow=(BLUE[2], .9, .1, .6))}
{command('top --languages', W / 2, 84, 20, BLUE)}
{''.join(rows)}
<text x="28" y="{H - 16}" font-family="{MONO}" font-size="11" fill="{TEXT_DIM}"># by code size · private repos too</text>'''
    label = 'Top languages: ' + ', '.join(f'{n} {sz / total * 100:.0f}%' for n, sz, _ in top)
    style = '''
.cell { animation: cell 5s ease-in-out infinite; }
@keyframes cell { 0%, 86%, 100% { opacity: 1; } 92% { opacity: .5; } }
'''
    return body, style, label


def streak_and_languages(s):
    """The streak and top languages windows side by side in one image, with a 12px gap."""
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
    print({k: v for k, v in s.items() if k not in ('months', 'langs', 'recent')})


if __name__ == '__main__':
    main()
