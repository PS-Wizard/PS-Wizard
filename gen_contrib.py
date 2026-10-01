#!/usr/bin/env python3
"""Make animated contribution SVG. Stdlib only. ponytail: one file."""
import json, os, sys, urllib.request, datetime

USER = os.environ.get("GH_USER", "PS-Wizard")
TOKEN = os.environ.get("GITHUB_TOKEN", "") or os.environ.get("GH_TOKEN", "")
OUT = os.path.join(os.path.dirname(__file__), "svg", "github-contrib-animated.svg")

Q = 'query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}'

def fetch():
    # ponytail: use live data if token exists, else use saved file
    if not TOKEN:
        d = json.load(open("/tmp/cal.json"))
        return d["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": Q, "variables": {"u": USER}}).encode(),
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)
    return d["data"]["user"]["contributionsCollection"]["contributionCalendar"]

def level(c):
    if c == 0: return 0
    if c <= 4: return 1
    if c <= 8: return 2
    if c <= 12: return 3
    return 4

os.makedirs(os.path.join(os.path.dirname(__file__), "svg"), exist_ok=True)
cal = fetch()
weeks, total = cal["weeks"], cal["totalContributions"]
fills = ['#161b22','#0e4429','#006d32','#26a641','#39d353']
GX, GY, CELL, GAP, STEP = 45, 40, 10, 3, 13
W, H = 750, 152

months, prev = [], None
for wi, w in enumerate(weeks):
    m = datetime.date.fromisoformat(w["contributionDays"][0]["date"]).month
    if m != prev and wi > 0:
        months.append((wi, datetime.date.fromisoformat(w["contributionDays"][0]["date"]).strftime('%b')))
    prev = m

p = []
p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">')
p.append('<title>GitHub contribution graph</title>')
p.append('''<style>
*{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
.bg{fill:#0d1117;stroke:#30363d;stroke-width:1}
.m{fill:#7d8590;font-size:10px;opacity:0;animation:fadeIn .6s ease forwards}
.d{fill:#7d8590;font-size:9px;opacity:0;animation:fadeIn .6s ease forwards}
.cell{transform-box:fill-box;transform-origin:center;opacity:0;animation:pop .45s cubic-bezier(.34,1.56,.64,1) forwards;animation-delay:var(--d)}
.hot{animation:pop .45s cubic-bezier(.34,1.56,.64,1) forwards,hotPulse 2.6s ease-in-out infinite;animation-delay:var(--d),calc(var(--d) + 700ms)}
.sweep{opacity:0;animation:sweep 7s ease-in-out infinite;animation-delay:4s}
@keyframes pop{0%{opacity:0;transform:scale(0)}60%{opacity:1;transform:scale(1.35)}100%{opacity:1;transform:scale(1)}}
@keyframes hotPulse{0%,100%{opacity:1;transform:scale(1);filter:brightness(1)}50%{opacity:1;transform:scale(1.18);filter:brightness(1.45) drop-shadow(0 0 3px rgba(57,211,83,.8))}}
@keyframes fadeIn{to{opacity:1}}
@keyframes sweep{0%{opacity:0;transform:translateX(-260px) skewX(-18deg)}8%{opacity:.16}22%{opacity:.16;transform:translateX(860px) skewX(-18deg)}23%,100%{opacity:0;transform:translateX(860px) skewX(-18deg)}}
@media (prefers-reduced-motion:reduce){.cell,.hot,.sweep,.m,.d{animation-duration:.01ms;animation-delay:0ms;animation-iteration-count:1}}
</style>''')
p.append(f'<rect class="bg" x="1" y="1" width="{W-2}" height="{H-2}" rx="6"/>')
for wi, name in months:
    p.append(f'<text class="m" x="{GX+wi*STEP}" y="28" style="animation-delay:{300+wi*28}ms">{name}</text>')
for row, name in {1:'Mon',3:'Wed',5:'Fri'}.items():
    p.append(f'<text class="d" x="12" y="{GY+row*STEP+CELL-1}" style="animation-delay:{300+row*60}ms">{name}</text>')
gw, gh = len(weeks)*STEP, 7*STEP
p.append(f'<clipPath id="gridClip"><rect x="{GX}" y="{GY}" width="{gw}" height="{gh}" rx="3"/></clipPath>')
for wi, w in enumerate(weeks):
    for di, day in enumerate(w["contributionDays"]):
        lv = level(day["contributionCount"])
        cls = "cell hot" if lv == 4 else "cell"
        p.append(f'<rect class="{cls}" x="{GX+wi*STEP}" y="{GY+di*STEP}" width="{CELL}" height="{CELL}" rx="2" fill="{fills[lv]}" style="--d:{(wi*7+di)*9}ms"><title>{day["date"]}: {day["contributionCount"]}</title></rect>')
p.append(f'<g clip-path="url(#gridClip)"><rect class="sweep" x="{GX-120}" y="{GY-20}" width="90" height="{gh+40}" fill="url(#shine)"/></g>')
p.append('<linearGradient id="shine" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".9"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')
p.append('</svg>')
open(OUT, "w").write("\n".join(p))
print(f"wrote {OUT} total={total}")

# --- header line outside graph: count + muted bracket tagline ---
import base64 as _b64
_fd = os.path.dirname(__file__)
_greg = _b64.b64encode(open(os.path.join(_fd, 'fonts', 'geist-reg.woff2'), 'rb').read()).decode()
_gmed = _b64.b64encode(open(os.path.join(_fd, 'fonts', 'geist-med.woff2'), 'rb').read()).decode()
_words = ['yes,', 'i', 'reviewed', "linus's", 'first', 'PR', 'in', '1980']
_spans = '<tspan class="hm hw" dx="10" style="--d:350ms">(</tspan>' + ''.join(f'<tspan class="hm hw" dx="5" style="--d:{480+i*130}ms">{w}</tspan>' for i, w in enumerate(_words)) + '<tspan class="hm hw" dx="5" style="--d:1650ms">)</tspan>'
_h = []
_h.append('<svg xmlns="http://www.w3.org/2000/svg" width="750" height="40" viewBox="0 0 750 40" role="img">')
_h.append(''.join([
  '<style>@font-face{font-family:Geist;src:url(data:font/woff2;base64,', _greg, ') format("woff2");font-weight:400}',
  '@font-face{font-family:Geist;src:url(data:font/woff2;base64,', _gmed, ') format("woff2");font-weight:500}',
  '*{font-family:Geist,Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}',
  '.hc{fill:#e6edf3;font-size:15px;font-weight:600;opacity:0;animation:hIn .6s ease forwards;animation-delay:50ms}',
  '.hm{fill:#7d8590;font-size:13px}',
  '.hw{opacity:0;animation:wIn .5s ease forwards;animation-delay:var(--d)}',
  '@keyframes hIn{from{opacity:0;transform:translateY(-4px)}to{opacity:1}}',
  '@keyframes wIn{from{opacity:0;transform:translateY(4px);filter:blur(2px)}to{opacity:1;transform:translateY(0);filter:blur(0)}}',
  '@media (prefers-reduced-motion:reduce){.hc,.hw{animation-duration:.01ms;animation-delay:0ms}}</style>']))
_h.append(f'<text x="4" y="25"><tspan class="hc">{total} contributions this year</tspan>{_spans}</text>')
_h.append('</svg>')
open(os.path.join(_fd, "svg", "graph-header.svg"), 'w').write(chr(10).join(_h))
print('wrote graph-header.svg')

# --- streak card, same style ---
days = sorted([d for w in weeks for d in w['contributionDays']], key=lambda x: x['date'])
cur = 0
ds = days[:-1] if days and days[-1]['contributionCount'] == 0 else days
for d in reversed(ds):
    if d['contributionCount'] > 0: cur += 1
    else: break
longest = run = 0
for d in days:
    run = run + 1 if d['contributionCount'] > 0 else 0
    longest = max(longest, run)
OUT2 = os.path.join(os.path.dirname(__file__), "svg", "github-streak-animated.svg")
s = []
s.append('<svg xmlns="http://www.w3.org/2000/svg" width="750" height="132" viewBox="0 0 750 132" role="img">')
s.append('<title>streak</title>')
s.append('''<style>*{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}.bg{fill:#0d1117;stroke:#30363d}.num{fill:#e6edf3;font-size:30px;font-weight:700}.lab{fill:#7d8590;font-size:11px;letter-spacing:1.5px}.stat{opacity:0;animation:up .6s ease forwards}.bar{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:fill 1s ease forwards}.fire{transform-box:fill-box;transform-origin:center;animation:flick 1.6s ease-in-out infinite}@keyframes up{from{opacity:0;transform:translateY(8px)}to{opacity:1}}@keyframes fill{to{transform:scaleX(1)}}@keyframes flick{0%,100%{transform:scale(1)}50%{transform:scale(1.15) rotate(-3deg)}}@media (prefers-reduced-motion:reduce){.stat,.bar,.fire{animation-duration:.01ms;animation-delay:0ms}}</style>''')
s.append('<rect class="bg" x="1" y="1" width="748" height="130" rx="6"/>')
s.append('<text x="60" y="34" fill="#7d8590" font-size="12">@%s — streak</text>' % USER)
s.append('<text x="690" y="36" text-anchor="end" font-size="20" class="fire">🔥</text>')
stats = [(str(total), 'TOTAL CONTRIBUTIONS', '#39d353', 100), (str(cur), 'CURRENT STREAK — DAYS', '#f0883e', 300), (str(longest), 'LONGEST STREAK — DAYS', '#26a641', 500)]
xs = [60, 300, 540]
bars = [min(total / 1500, 1.0), min(cur / 30, 1.0), min(longest / 31, 1.0)]
for i, (n, lab, col, dl) in enumerate(stats):
    x = xs[i]
    s.append(f'<g class="stat" style="animation-delay:{dl}ms"><text class="num" x="{x}" y="88">{n}</text><text class="lab" x="{x}" y="108">{lab}</text></g>')
    bw = int(150 * bars[i])
    s.append(f'<rect x="{x}" y="114" width="150" height="4" rx="2" fill="#21262d"/><rect class="bar" x="{x}" y="114" width="{max(bw, 6)}" height="4" rx="2" fill="{col}" style="animation-delay:{dl + 400}ms"/>')
s.append('</svg>')
open(OUT2, 'w').write("\n".join(s))
print(f"wrote {OUT2} cur={cur} longest={longest}")
