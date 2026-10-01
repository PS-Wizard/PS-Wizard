#!/usr/bin/env python3
"""Make animated contribution SVG. Stdlib only. ponytail: one file."""
import json, os, sys, urllib.request, datetime

USER = os.environ.get("GH_USER", "PS-Wizard")
TOKEN = os.environ.get("GITHUB_TOKEN", "") or os.environ.get("GH_TOKEN", "")
OUT = os.path.join(os.path.dirname(__file__), "github-contrib-animated.svg")

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

cal = fetch()
weeks, total = cal["weeks"], cal["totalContributions"]
fills = ['#161b22','#0e4429','#006d32','#26a641','#39d353']
GX, GY, CELL, GAP, STEP = 45, 62, 10, 3, 13
W, H = 750, 200

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
.h-title{fill:#e6edf3;font-size:14px;font-weight:600;opacity:0;animation:fadeDown .7s ease forwards;animation-delay:50ms}
.h-user{fill:#7d8590;font-size:12px;opacity:0;animation:fadeDown .7s ease forwards;animation-delay:150ms}
.m{fill:#7d8590;font-size:10px;opacity:0;animation:fadeIn .6s ease forwards}
.d{fill:#7d8590;font-size:9px;opacity:0;animation:fadeIn .6s ease forwards}
.cell{transform-box:fill-box;transform-origin:center;opacity:0;animation:pop .45s cubic-bezier(.34,1.56,.64,1) forwards;animation-delay:var(--d)}
.hot{animation:pop .45s cubic-bezier(.34,1.56,.64,1) forwards,hotPulse 2.6s ease-in-out infinite;animation-delay:var(--d),calc(var(--d) + 700ms)}
.legend{opacity:0;animation:fadeUp .6s ease forwards;animation-delay:3400ms}
.legend-t{fill:#7d8590;font-size:10px}
.sweep{opacity:0;animation:sweep 7s ease-in-out infinite;animation-delay:4s}
@keyframes pop{0%{opacity:0;transform:scale(0)}60%{opacity:1;transform:scale(1.35)}100%{opacity:1;transform:scale(1)}}
@keyframes hotPulse{0%,100%{opacity:1;transform:scale(1);filter:brightness(1)}50%{opacity:1;transform:scale(1.18);filter:brightness(1.45) drop-shadow(0 0 3px rgba(57,211,83,.8))}}
@keyframes fadeIn{to{opacity:1}}
@keyframes fadeUp{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
@keyframes fadeDown{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:translateY(0)}}
@keyframes sweep{0%{opacity:0;transform:translateX(-260px) skewX(-18deg)}8%{opacity:.16}22%{opacity:.16;transform:translateX(860px) skewX(-18deg)}23%,100%{opacity:0;transform:translateX(860px) skewX(-18deg)}}
@media (prefers-reduced-motion:reduce){.cell,.hot,.sweep,.legend,.h-title,.h-user,.m,.d{animation-duration:.01ms;animation-delay:0ms;animation-iteration-count:1}}
</style>''')
p.append(f'<rect class="bg" x="1" y="1" width="{W-2}" height="{H-2}" rx="6"/>')
p.append(f'<text class="h-title" x="16" y="30">{total} contributions in the last year</text>')
p.append(f'<text class="h-user" x="{W-16}" y="30" text-anchor="end">@{USER}</text>')
for wi, name in months:
    p.append(f'<text class="m" x="{GX+wi*STEP}" y="52" style="animation-delay:{300+wi*28}ms">{name}</text>')
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
lx, ly = GX+gw-150, GY+gh+22
p.append(f'<g class="legend"><text class="legend-t" x="{lx}" y="{ly+8}">Less</text>')
for i, f in enumerate(fills):
    p.append(f'<rect x="{lx+32+i*13}" y="{ly}" width="10" height="10" rx="2" fill="{f}"/>')
p.append(f'<text class="legend-t" x="{lx+32+5*13+4}" y="{ly+8}">More</text></g>')
p.append('</svg>')
open(OUT, "w").write("\n".join(p))
print(f"wrote {OUT} total={total}")
