#!/usr/bin/env python3
"""One-shot: icon cloud. Best-of-seeds pack, black sticker outline, strong glow."""
import re, os, random
HERE = os.path.dirname(__file__)
ICON_DIR = os.path.join(HERE, "icons-svg")
COLORS = {
    "rust": "#CE422B", "go": "#00ADD8", "svelte": "#FF3E00",
    "python": "#3776AB", "javascript": "#F7DF1E", "react": "#61DAFB",
    "solid": "#5A8DE0", "htmx": "#4C7DE0", "c": "#A8B9CC",
    "cplusplus": "#2E9BDB", "gnubash": "#4EAA25", "lua": "#7C8DB5",
    "mysql": "#5B9BD1", "postgresql": "#4169E1", "sqlite": "#0F9BD8",
    "html5": "#E34F26", "css": "#663399", "typescript": "#3178C6",
    "docker": "#2496ED", "typst": "#239DAD", "mermaid": "#FF3670",
}

def path(name):
    t = open(os.path.join(ICON_DIR, name + ".svg")).read()
    return re.search(r'<path d="([^"]+)', t).group(1)

W, H = 750, 300
NAMES = (["rust", "go", "svelte"]
         + ["python", "javascript", "typescript", "react", "solid", "htmx", "html5", "css",
            "c", "cplusplus", "gnubash", "lua", "mysql", "postgresql", "sqlite",
            "docker", "typst", "mermaid"])
BASE = {"rust": 86, "go": 78, "svelte": 78}

def layout(seed):
    rng = random.Random(seed)
    sizes = dict(BASE)
    for n in NAMES[3:]:
        sizes[n] = rng.randint(34, 52)
    placed = []
    def spot(size):
        for _ in range(3000):
            x = rng.uniform(70 + size/2, W - 70 - size/2)
            y = rng.uniform(22 + size/2, H - 22 - size/2)
            if all(((x-px)**2 + (y-py)**2) ** .5 > (size+ps)/2 * 1.12 for px, py, ps in placed):
                return x, y
        return None
    items = []
    for name in NAMES:
        r = spot(sizes[name])
        if r is None:
            return None
        placed.append((r[0], r[1], sizes[name])); items.append((name, r[0], r[1], sizes[name]))
    return items

def score(items):
    # smallest big-empty-gap wins; keep mass near center
    worst = 0
    x = 70
    while x < W - 70:
        y = 22
        while y < H - 22:
            d = min(((x-ix)**2 + (y-iy)**2) ** .5 - s/2 for _, ix, iy, s in items)
            worst = max(worst, d)
            y += 25
        x += 25
    cx = sum(ix for _, ix, _, _ in items) / len(items)
    cy = sum(iy for _, _, iy, _ in items) / len(items)
    return worst + 0.4 * (((cx - W/2) ** 2 + (cy - H/2) ** 2) ** .5)

best, bestscore = None, 1e9
for seed in range(80):
    items = layout(seed)
    if items is None:
        continue
    s = score(items)
    if s < bestscore:
        best, bestscore, bestseed = items, s, seed
print("best seed", bestseed, "gap", round(bestscore, 1))
items = best

rng = random.Random(99)
delays = [rng.randint(100, 1700) for _ in items]
p = []
p.append('<svg xmlns="http://www.w3.org/2000/svg" width="750" height="300" viewBox="0 0 750 300" role="img">')
p.append('<title>stack cloud</title>')
p.append('''<style>
.mi{transform-box:fill-box;transform-origin:center;filter:drop-shadow(0 0 12px var(--g));opacity:0;animation:pop .5s cubic-bezier(.34,1.56,.64,1) forwards,float 4s ease-in-out infinite;animation-delay:var(--d),calc(var(--d) + 900ms)}
.halo{fill:#000;transform-box:fill-box;transform-origin:center;opacity:0;animation:pop .5s cubic-bezier(.34,1.56,.64,1) forwards;animation-delay:var(--d)}
.sp{fill:#39d353;transform-box:fill-box;transform-origin:center;opacity:0;animation:tw 2.2s ease-in-out infinite;animation-delay:var(--d)}
@keyframes pop{0%{opacity:0;transform:scale(0)}60%{opacity:1;transform:scale(1.3)}100%{opacity:1;transform:scale(1)}}
@keyframes float{0%,100%{translate:0 0}50%{translate:0 -5px}}
@keyframes tw{0%,100%{opacity:.2;transform:scale(.7)}50%{opacity:1;transform:scale(1.1)}}
@media (prefers-reduced-motion:reduce){.mi,.halo,.sp{animation-duration:.01ms;animation-delay:0ms;animation-iteration-count:1}}
</style>''')
p.append('<rect x="1" y="1" width="748" height="298" rx="6" fill="#0d1117" stroke="#30363d"/>')
for (name, x, y, s), d in zip(items, delays):
    k = s / 24
    p.append(f'<g transform="translate({x-12*k:.1f},{y-12*k:.1f}) scale({k:.3f})">'
             f'<g transform="translate(12,12) scale(1.05) translate(-12,-12)">'
             f'<path class="halo" style="--d:{d}ms" d="{path(name)}"/></g>'
             f'<path class="mi" style="--d:{d}ms;--g:{COLORS[name]}" d="{path(name)}" fill="{COLORS[name]}">'
             f'<title>{name}</title></path></g>')
for (x, y, d) in [(40, 24, 500), (710, 26, 800), (710, 274, 1100), (40, 274, 1300)]:
    p.append(f'<path class="sp" style="--d:{d}ms" transform="translate({x},{y})" d="M0,-8 C1,-2 2,-1 8,0 C2,1 1,2 0,8 C-1,2 -2,1 -8,0 C-2,-1 -1,-2 0,-8 Z"/>')
p.append('</svg>')
out = os.path.join(HERE, "svg", "stack-cloud.svg")
open(out, "w").write("\n".join(p))
print("wrote", out)
