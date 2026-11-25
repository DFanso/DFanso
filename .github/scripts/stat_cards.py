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

HEAT_WEEKS = 20  # how many weeks the streak card's heatmap shows


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
  contributionsCollection { contributionYears }
} }'''

# Every owned non-fork repo, 100 a page, for the stars and language totals.
REPOS_QUERY = '''query($login: String!, $after: String) { user(login: $login) {
  repositories(first: 100, after: $after, ownerAffiliations: OWNER, isFork: false) {
    pageInfo { hasNextPage endCursor }
    nodes {
      stargazerCount
      primaryLanguage { name color }
      languages(first: 10, orderBy: { field: SIZE, direction: DESC }) { edges { size node { name color } } }
    }
  }
} }'''


def owned_repos(login):
    repos, after = [], None
    while True:
        page = gql(REPOS_QUERY, login=login, after=after)['user']['repositories']
        repos += page['nodes']
        if not page['pageInfo']['hasNextPage']:
            return repos
        after = page['pageInfo']['endCursor']


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
    for r in owned_repos(login):
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
        # Every day of the last HEAT_WEEKS weeks (Monday to Sunday, the current week last), for the heatmap.
        'recent': {d: days.get(d, 0) for d in (today - dt.timedelta(days=today.weekday() + 7 * (HEAT_WEEKS - 1) - k)
                                                for k in range(7 * HEAT_WEEKS)) if d <= today},
        'last_active': max((d for d in order if days[d]), default=None),
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
        ('calendar-days', AMBER, s['year'], f"contributions_{s['today'].year}"),
    ]
    tw, th, gap, tx0, ty0 = 155, 80, 12, 320, 60
    out = []
    for i, (icon, col, value, label) in enumerate(tiles):
        x, y = tx0 + (i % 4) * (tw + gap), ty0 + (i // 4) * (th + gap)
        # A label too long for the tile at 11.5px (mono, .6em a character, colon included) is set
        # smaller so it ends 12px inside the edge.
        ls = min(11.5, (tw - 36 - 12) / ((len(label) + 1) * .6))
        out.append(f'''<g transform="translate({x} {y})">{raised(0, 0, tw, th, 10, CARD, LIP, 5, EDGE)}
  <rect x="0" y="12" width="3" height="20" rx="1.5" fill="{col[1]}"/>
  {glyph(icon, 14, 14, 15, col[1], 2.2)}
  <text x="36" y="26" font-family="{MONO}" font-size="{ls:g}" font-weight="700" fill="{TEXT_DIM}">{esc(label)}<tspan fill="{TEXT_DIM}">:</tspan></text>
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
    label = (f"{s['total']:,} lifetime contributions, {s['year']:,} contributions this year. Pull requests {s['prs']:,}, issues {s['issues']:,}, "
             f"contributed to {s['contributed']} repos, {s['stars']} stars, {s['repos']} repositories, {s['followers']} followers, {fmt(s['views'])} profile views.")
    return svg(W, H + PAD, label, body)


PANEL_H = 330


def short(d, today):
    """A date as "Nov 16", with the year only when it isn't this year."""
    return f"{d:%b} {d.day}" + ('' if d.year == today.year else f" '{d:%y}")


def fit(text, width, size):
    """The font size (at most `size`) at which monospace `text` fits in `width`."""
    return round(min(size, width / (max(len(text), 1) * .6)), 2)


HEAT = (SLOT, '#2d4a3e', '#41704a', '#73a14a', GREEN[1])  # none, then four levels


def heatmap(s, x, y, cell=13, gap=3):
    """The last HEAT_WEEKS weeks as a GitHub-style grid (a column a week, Monday on top), shaded
    by quartiles of the active days. The current streak's days are outlined and today is ringed."""
    days, today = s['recent'], s['today']
    step = cell + gap
    start = min(days)
    active = sorted(n for n in days.values() if n)
    cuts = [active[min(len(active) - 1, int(len(active) * q))] for q in (.25, .5, .75)] if active else []
    streak = set()
    if s['current_range']:
        a, b = s['current_range']
        streak = {d for d in days if a <= d <= b}
    out, months, last_col = [], [], -9
    for d, n in sorted(days.items()):
        col, row = (d - start).days // 7, d.weekday()
        cx, cy = x + col * step, y + row * step
        level = 0 if not n else 1 + sum(n > c for c in cuts)
        out.append(f'<rect x="{cx}" y="{cy}" width="{cell}" height="{cell}" rx="2.5" fill="{HEAT[level]}"/>')
        if d in streak:
            out.append(f'<rect x="{cx - 1}" y="{cy - 1}" width="{cell + 2}" height="{cell + 2}" rx="3.5" fill="none" stroke="{CYAN[0]}" stroke-width="1.6"/>')
        if d == today:
            out.append(f'<rect x="{cx - 2.5}" y="{cy - 2.5}" width="{cell + 5}" height="{cell + 5}" rx="4.5" fill="none" stroke="{AMBER[1]}" stroke-width="2"/>')
        # A month's name over the first column that starts in it, unless it would crowd the last one.
        if row == 0 and (d.day <= 7) and col - last_col >= 3:
            months.append(f'<text x="{cx}" y="{y - 8}" font-family="{MONO}" font-size="12.5" fill="{TEXT_SOFT}">{d:%b}</text>')
            last_col = col
    labels = ''.join(f'<text x="{x - 8}" y="{y + r * step + cell - 2}" font-family="{MONO}" font-size="12" fill="{TEXT_DIM}" text-anchor="end">{t}</text>'
                     for r, t in ((0, 'Mon'), (2, 'Wed'), (4, 'Fri'), (6, 'Sun')))
    return ''.join(months) + labels + ''.join(out)


def streak(s):
    W, H = 494, PANEL_H - DEPTH
    today = s['today']

    def stat(x, w, label, value, unit, sub, col, size=26):
        unit_ = f'<tspan dx="7" font-size="15" font-weight="700" fill="{TEXT_SOFT}">{unit}</tspan>' if unit else ''
        return (f'<g transform="translate({x} 50)">{raised(0, 0, w, 100, 10, CARD, LIP, 5, EDGE)}'
                f'<rect x="0" y="12" width="3" height="20" rx="1.5" fill="{col[1]}"/>'
                f'<text x="14" y="27" font-family="{MONO}" font-size="13" font-weight="700" fill="{TEXT_SOFT}">{esc(label)}</text>'
                f'<text x="14" y="{36 + size * .8:.0f}" font-family="{MONO}" font-size="{size}" font-weight="800" fill="{col[0]}">{esc(value)}{unit_}</text>'
                f'<text x="14" y="88" font-family="{MONO}" font-size="{fit(sub, w - 26, 13):g}" fill="{TEXT_DIM}">{esc(sub)}</text></g>')

    days = lambda n: 'day' if n == 1 else 'days'
    if s['current']:
        a, _ = s['current_range']
        hero = stat(20, 160, 'Current streak', str(s['current']), days(s['current']), f'since {short(a, today)}', CYAN, 36)
    else:
        last = s['last_active']
        hero = stat(20, 160, 'No streak now', '0', 'days', f'last active {short(last, today)}' if last else 'start one today', CYAN, 36)
    la, lb = s['longest_range'] if s['longest_range'][0] else (None, None)
    longest = stat(188, 146, 'Longest streak', str(s['longest']), days(s['longest']),
                   (short(la, today) if la == lb else f'{short(la, today)} – {short(lb, today)}') if la else '–', PURPLE)
    total = stat(342, 132, 'Contributions', fmt(s['total']), '', f"since {s['joined']:%b %Y}", BLUE)

    cell, gap = 12, 3
    grid_w = HEAT_WEEKS * (cell + gap) - gap
    gx = round((W - grid_w) / 2 + 16)
    legend_y = 306
    shades = ''.join(f'<rect x="{gx + 44 + k * 15}" y="{legend_y - 11}" width="12" height="12" rx="2.5" fill="{c}"/>' for k, c in enumerate(HEAT))
    lx = gx + grid_w
    legend = (f'<text x="{gx}" y="{legend_y}" font-family="{MONO}" font-size="12" fill="{TEXT_DIM}">less</text>{shades}'
              f'<text x="{gx + 44 + 5 * 15 + 5}" y="{legend_y}" font-family="{MONO}" font-size="12" fill="{TEXT_DIM}">more</text>'
              f'<rect x="{lx - 132}" y="{legend_y - 11}" width="13" height="13" rx="3" fill="none" stroke="{CYAN[0]}" stroke-width="1.6"/>'
              f'<text x="{lx - 113}" y="{legend_y}" font-family="{MONO}" font-size="12" fill="{TEXT_DIM}">streak</text>'
              f'<rect x="{lx - 60}" y="{legend_y - 12}" width="15" height="15" rx="4" fill="none" stroke="{AMBER[1]}" stroke-width="2"/>'
              f'<text x="{lx}" y="{legend_y}" font-family="{MONO}" font-size="12" fill="{TEXT_DIM}" text-anchor="end">today</text>')
    body = f'''{window(W, H, '~/streak — git log --streak', 'st', glow=(GREEN[2], .2, .2, .6))}
{hero}{longest}{total}
{heatmap(s, gx, 186, cell, gap)}
{legend}'''
    label = (f"Contribution streak: {s['current']} days now, longest {s['longest']} days, {s['total']:,} contributions in total. "
             f"A heatmap shows the last {HEAT_WEEKS} weeks.")
    return body, '', label


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
    print({k: v for k, v in s.items() if k not in ('langs', 'recent')})


if __name__ == '__main__':
    main()
