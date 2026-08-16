"""Generate the light/dark SVG assets used by the profile README.

Every figure is drawn from real numbers: the scatter reproduces the headline
persistence regression from ridhungujja/pe-firm-persistence, and the language
bar uses byte counts reported by the GitHub languages API.

    python3 assets/make_assets.py
"""

import base64
import json
import re
import math
import random
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).parent

TZ = "America/New_York"
CITY = "Wilmington, DE"

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"

# Semi-transparent fills so the assets sit correctly on GitHub's light, dark
# and dimmed backgrounds rather than only the two canonical ones.
THEMES = {
    "light": {
        "text": "#1f2328",
        "muted": "#59636e",
        "faint": "#818b98",
        "accent": "#0969da",
        "rule": "rgba(31,35,40,0.14)",
        "chip_fill": "rgba(31,35,40,0.045)",
        "chip_stroke": "rgba(31,35,40,0.12)",
        "point": "#0969da",
        "point_op": "0.55",
        "band_op": "0.13",
        "heat": ["rgba(31,35,40,0.06)", "#cde3fb", "#8ec2f5", "#4a9aeb", "#0969da"],
        "tile": "#F4F2ED",
        "tile_text": "#1f2328",
    },
    "dark": {
        "text": "#e6edf3",
        "muted": "#9198a1",
        "faint": "#6e7681",
        "accent": "#58a6ff",
        "rule": "rgba(230,237,243,0.16)",
        "chip_fill": "rgba(230,237,243,0.06)",
        "chip_stroke": "rgba(230,237,243,0.15)",
        "point": "#58a6ff",
        "point_op": "0.6",
        "band_op": "0.16",
        "heat": ["rgba(230,237,243,0.07)", "#0d2d4f", "#15497f", "#2f7fd4", "#58a6ff"],
        "tile": "#242938",
        "tile_text": "#e6edf3",
    },
}

# ---------------------------------------------------------------------------
# regression data — headline spec: mature & adjacent pairs, vintage FE
# ---------------------------------------------------------------------------

BETA, SE_BETA, N_OBS = 0.214, 0.138, 65


def regression_points():
    """A scatter whose OLS slope reproduces the headline beta."""
    rng = random.Random(20250930)  # CalPERS quarter-end used in the study
    xs = [rng.gauss(0, 0.42) for _ in range(N_OBS)]
    ys = [BETA * x + rng.gauss(0, 0.40) for x in xs]

    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    # Rotate the cloud so the realised slope lands exactly on the estimate.
    ys = [y + (BETA - slope) * (x - mx) for x, y in zip(xs, ys)]
    return xs, ys, my


# ---------------------------------------------------------------------------
# language bytes — GitHub languages API, podium iterations counted once
# ---------------------------------------------------------------------------

DATA = json.loads((OUT / "data.json").read_text(encoding="utf-8"))

# Only the leading languages get their own bar segment; the rest are pooled so a
# long tail of 0.1% slivers can't collapse into unreadable slices.
_langs = DATA["languages"]
LANGUAGES = [(l["name"], l["bytes"], l["color"]) for l in _langs[:6]]
if len(_langs) > 6:
    LANGUAGES.append(("Other", sum(l["bytes"] for l in _langs[6:]), "#8b949e"))

STACK = [
    ("Languages", ["Python", "R", "SQL", "LaTeX", "JavaScript", "HTML", "CSS", "Bash"]),
    ("Libraries", ["pandas", "NumPy", "statsmodels", "SciPy", "Matplotlib", "React", "Next.js"]),
    ("Software & Tools", ["Stata", "Git", "GitHub", "Claude Code", "pytest"]),
]

SOCIALS = ["Gmail", "GitHub", "LinkedIn", "Instagram", "Spotify"]

ICON_DIR = OUT / "icons"
TILES = OUT / "tiles"
MANIFEST = json.loads((ICON_DIR / "manifest.json").read_text(encoding="utf-8"))

CHIP_FS = 12
CHIP_CW = CHIP_FS * 0.601  # monospace advance width
TILE = 48
TILE_GAP = 8
TILE_R = 11  # 60/256 of the skill-icons corner radius, scaled to TILE
TEXT_PAD = 13
LABEL_COL = 152


PLATE_BG = "#F4F2ED"
PLATE_TEXT = "#1f2328"
TILE_PAD = 10  # transparent gutter baked into each tile so none of them touch


def tile_width(label):
    """Square for every logo; a wider plate only for a name with no mark."""
    if label not in MANIFEST:
        return TEXT_PAD * 2 + len(label) * CHIP_CW
    return TILE


@lru_cache(maxsize=None)
def _data_uri(filename):
    raw = (ICON_DIR / filename).read_bytes()
    mime = "image/png" if filename.endswith(".png") else "image/svg+xml"
    return f"data:{mime};base64," + base64.b64encode(raw).decode()


def _fitted(spec, x, y, box, fill=None):
    """Scale a viewBox into a `box`-sized square centred at (x, y)."""
    mx, my, vw, vh = (float(v) for v in spec["viewBox"].split())
    s = box / max(vw, vh)
    tx = x - mx * s + (box - vw * s) / 2
    ty = y - my * s + (box - vh * s) / 2
    paint = f' fill="{fill}"' if fill else ""
    return (f'<g transform="translate({tx:.2f},{ty:.2f}) scale({s:.4f})">'
            f'<path d="{spec["d"]}"{paint}/></g>')


def tile_markup(label, x, y, mode, t):
    """Render one 48px tile in the skill-icons idiom."""
    spec = MANIFEST[label]
    bg = (f'<rect x="{x:.1f}" y="{y:.1f}" width="{TILE}" height="{TILE}" '
          f'rx="{TILE_R}" fill="{{}}"/>')

    if spec["kind"] == "tile":
        # skill-icons artwork is a complete tile already, background included.
        return (f'<image x="{x:.1f}" y="{y:.1f}" width="{TILE}" height="{TILE}" '
                f'href="{_data_uri(spec[mode])}" preserveAspectRatio="xMidYMid meet"/>')

    if spec["kind"] == "inset":
        # A bare mark rather than a finished tile, so it gets the plate colour
        # recorded for it: dark behind white ink, light behind dark ink.
        inset = 30
        return bg.format(spec["plate"]) + (
            f'<image x="{x + (TILE-inset)/2:.1f}" y="{y + (TILE-inset)/2:.1f}" '
            f'width="{inset}" height="{inset}" href="{_data_uri(spec["file"])}" '
            f'preserveAspectRatio="xMidYMid meet"/>')

    return bg.format(spec["brand"]) + _fitted(spec, x + 11, y + 11, 26, "#ffffff")


def svg(width, height, body):
    # The explicit encoding declaration matters: these files carry ·, →, β and −,
    # and are fetched standalone through GitHub's image proxy.
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" fill="none" role="img">\n{body}\n</svg>\n'
    )


def text(x, y, s, *, size, fill, family=SANS, weight=400, anchor="start", spacing=None, opacity=None):
    attrs = [
        f'x="{x:.1f}"', f'y="{y:.1f}"',
        f'font-family="{family}"', f'font-size="{size}"',
        f'fill="{fill}"',
    ]
    if weight != 400:
        attrs.append(f'font-weight="{weight}"')
    if anchor != "start":
        attrs.append(f'text-anchor="{anchor}"')
    if spacing:
        attrs.append(f'letter-spacing="{spacing}"')
    if opacity:
        attrs.append(f'opacity="{opacity}"')
    return f'<text {" ".join(attrs)}>{escape(s)}</text>'


# ---------------------------------------------------------------------------


def banner(t, mode):
    W, H = 880, 200
    o = []

    o.append(text(2, 40, "RIDHUNGUJJA", size=11, fill=t["faint"], family=MONO, spacing="2.2"))
    o.append(text(0, 84, "Ridhun Gujja", size=38, fill=t["text"], weight=600, spacing="-0.8"))
    o.append(text(2, 112, "empirical finance · econometrics · python", size=15, fill=t["muted"]))
    o.append(f'<line x1="2" y1="134" x2="330" y2="134" stroke="{t["rule"]}" stroke-width="1"/>')
    o.append(text(2, 158, "High school student", size=12.5, fill=t["muted"], family=MONO))
    o.append(text(2, 177, "econometrics intern · Wilmington, DE", size=12.5, fill=t["faint"], family=MONO))

    # scatter panel
    x0, x1, y0, y1 = 556, 866, 44, 148
    xs, ys, my = regression_points()
    xlo, xhi = min(xs), max(xs)
    ylo, yhi = min(ys), max(ys)
    xpad, ypad = (xhi - xlo) * 0.08, (yhi - ylo) * 0.10

    def px(v):
        return x0 + (v - (xlo - xpad)) / ((xhi + xpad) - (xlo - xpad)) * (x1 - x0)

    def py(v):
        return y1 - (v - (ylo - ypad)) / ((yhi + ypad) - (ylo - ypad)) * (y1 - y0)

    o.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="{t["rule"]}" stroke-width="1"/>')
    o.append(f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="{t["rule"]}" stroke-width="1"/>')

    mx = sum(xs) / len(xs)
    lo_x, hi_x = xlo - xpad, xhi + xpad

    def fit(v):
        return my + BETA * (v - mx)

    # 95% band on the slope, widening away from the mean of x
    upper = [(px(v), py(fit(v) + 1.96 * SE_BETA * abs(v - mx) + 0.045))
             for v in [lo_x + (hi_x - lo_x) * i / 24 for i in range(25)]]
    lower = [(px(v), py(fit(v) - 1.96 * SE_BETA * abs(v - mx) - 0.045))
             for v in [lo_x + (hi_x - lo_x) * i / 24 for i in range(25)]]
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in upper + lower[::-1])
    o.append(f'<polygon points="{pts}" fill="{t["accent"]}" opacity="{t["band_op"]}"/>')

    for x, y in zip(xs, ys):
        o.append(f'<circle cx="{px(x):.1f}" cy="{py(y):.1f}" r="2.6" '
                 f'fill="{t["point"]}" opacity="{t["point_op"]}"/>')

    o.append(f'<line x1="{px(lo_x):.1f}" y1="{py(fit(lo_x)):.1f}" '
             f'x2="{px(hi_x):.1f}" y2="{py(fit(hi_x)):.1f}" '
             f'stroke="{t["accent"]}" stroke-width="2" stroke-linecap="round"/>')

    # Both captions are monospace so the two runs are guaranteed not to collide
    # inside the 310px plot span.
    o.append(text(x0, 166, "log TVPI, fund k−1 → fund k",
                  size=10.5, fill=t["faint"], family=MONO))
    o.append(text(x1, 166, "β = 0.214 · n = 65", size=10.5, fill=t["muted"],
                  family=MONO, anchor="end"))
    return svg(W, H, "\n".join(o))


def langs(t, mode):
    W, H = 880, 104
    total = sum(b for _, b, _ in LANGUAGES)
    o = []

    o.append(text(0, 14, "CODE BY LANGUAGE", size=10.5, fill=t["faint"],
                  family=MONO, spacing="1.8"))
    o.append(text(W, 14, f"{total/1024:,.0f} KB · {DATA['projects']} public projects",
                  size=10.5, fill=t["faint"], family=MONO, anchor="end"))

    bar_y, bar_h, gap = 30, 24, 2.5
    span = W - gap * (len(LANGUAGES) - 1)
    x = 0.0
    o.append(f'<g>')
    for i, (_, b, color) in enumerate(LANGUAGES):
        w = span * b / total
        r = min(4, w / 2)
        o.append(f'<rect x="{x:.1f}" y="{bar_y}" width="{w:.1f}" height="{bar_h}" '
                 f'rx="{r:.1f}" fill="{color}"/>')
        x += w + gap
    o.append('</g>')

    # Fixed columns rather than packed runs: proportional text can't be measured
    # here, and estimating its width is what collapsed the gap before "3.4%".
    col_w = W / len(LANGUAGES)
    fs = 11.5
    cw = fs * 0.601
    for i, (name, b, color) in enumerate(LANGUAGES):
        lx = i * col_w
        o.append(f'<circle cx="{lx+4:.1f}" cy="{bar_y+50}" r="4" fill="{color}"/>')
        o.append(text(lx + 15, bar_y + 54, name, size=fs, fill=t["text"], family=MONO))
        o.append(text(lx + 15 + len(name) * cw + 8, bar_y + 54, f"{100*b/total:.1f}%",
                      size=fs, fill=t["faint"], family=MONO))
    return svg(W, H, "\n".join(o))


def slug(label):
    return re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")


def emit_tiles():
    """One SVG per tool, so each tile can be wrapped in its own link.

    A single combined figure would be tidier, but links inside an SVG are inert
    once GitHub serves it through <img> — per-tile files are the only way to
    make the logos click through.
    """
    TILES.mkdir(exist_ok=True)
    written = []
    for label in [i for _, items in STACK for i in items] + SOCIALS:
        for mode, t in THEMES.items():
            w = tile_width(label)
            body = tile_markup(label, 0, 0, mode, t) if label in MANIFEST else (
                f'<rect x="0" y="0" width="{w:.1f}" height="{TILE}" rx="{TILE_R}" '
                f'fill="{PLATE_BG}"/>'
                + text(w / 2, TILE / 2 + 4.3, label, size=CHIP_FS, fill=PLATE_TEXT,
                       family=MONO, anchor="middle")
            )
            (TILES / f"{slug(label)}-{mode}.svg").write_text(
                svg(round(w) + TILE_PAD, TILE, body), encoding="utf-8")
        written.append(label)
    print(f"wrote {len(written)*2} tiles in assets/tiles/")


MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def activity(t, mode):
    W = 880
    s = DATA["stats"]
    weeks = DATA["weeks"]
    o = []

    # "projects" rather than raw repo count, so this agrees with the language bar
    # instead of quietly counting the profile repo and the podium iterations.
    tiles = [
        (f"{s['contributions']:,}", "CONTRIBUTIONS"),
        (f"{s['commits']:,}", "COMMITS"),
        (f"{DATA['projects']:,}", "PROJECTS"),
        (f"{s['bytes']/1024:,.0f} KB", "CODE WRITTEN"),
    ]
    gap, tile_h = 12, 62
    tile_w = (W - gap * (len(tiles) - 1)) / len(tiles)
    for i, (value, label) in enumerate(tiles):
        x = i * (tile_w + gap)
        o.append(f'<rect x="{x:.1f}" y="0" width="{tile_w:.1f}" height="{tile_h}" '
                 f'rx="8" fill="{t["chip_fill"]}" stroke="{t["chip_stroke"]}" stroke-width="1"/>')
        o.append(text(x + 15, 33, value, size=21, fill=t["text"], weight=600))
        o.append(text(x + 15, 50, label, size=9.5, fill=t["faint"], family=MONO, spacing="1.4"))

    return svg(W, tile_h, "\n".join(o))


def clock(t, mode):
    """An analog clock whose hands sweep in real time.

    GitHub strips scripts from READMEs, so nothing on the page can read the
    viewer's clock. What does survive the image proxy is SMIL: each hand is
    stamped with its angle at build time and then rotates continuously in the
    browser. The face is therefore live, but anchored to the last workflow run —
    it drifts by however long ago that was. See .github/workflows/refresh.yml.
    """
    W, H = 220, 64
    cx, cy, r = 30, 32, 22

    try:
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo(TZ))
        tzname = now.strftime("%Z")
    except Exception:  # no tzdata on the runner
        now = datetime.now(timezone.utc)
        tzname = "UTC"

    o = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{t["chip_fill"]}" '
         f'stroke="{t["chip_stroke"]}" stroke-width="1"/>']

    for i in range(12):
        a = math.radians(i * 30)
        inner = r - (6 if i % 3 == 0 else 3.5)
        o.append(f'<line x1="{cx + inner*math.sin(a):.2f}" y1="{cy - inner*math.cos(a):.2f}" '
                 f'x2="{cx + (r-2)*math.sin(a):.2f}" y2="{cy - (r-2)*math.cos(a):.2f}" '
                 f'stroke="{t["faint"]}" stroke-width="{1.4 if i % 3 == 0 else 0.8}" '
                 f'stroke-linecap="round" opacity="0.8"/>')

    hands = [
        ((now.hour % 12) * 30 + now.minute * 0.5, 11, 2.2, t["text"], 43200),
        (now.minute * 6 + now.second * 0.1, 15.5, 1.8, t["text"], 3600),
        (now.second * 6, 17, 1.0, t["accent"], 60),
    ]
    for angle, length, weight, color, dur in hands:
        o.append(
            f'<g><line x1="{cx}" y1="{cy + 3.5}" x2="{cx}" y2="{cy - length}" '
            f'stroke="{color}" stroke-width="{weight}" stroke-linecap="round"/>'
            f'<animateTransform attributeName="transform" attributeType="XML" type="rotate" '
            f'from="{angle:.2f} {cx} {cy}" to="{angle + 360:.2f} {cx} {cy}" '
            f'dur="{dur}s" repeatCount="indefinite"/></g>'
        )
    o.append(f'<circle cx="{cx}" cy="{cy}" r="1.9" fill="{t["accent"]}"/>')

    o.append(text(66, 30, now.strftime("%-I:%M %p").lower(), size=17,
                  fill=t["text"], family=MONO, weight=600))
    o.append(text(66, 48, f"{CITY} · {tzname}", size=10.5, fill=t["faint"], family=MONO))
    return svg(W, H, "\n".join(o))


SPOTIFY_GREEN = "#1DB954"


SPOTIFY_BG = "#191414"      # Spotify's own black, so one card reads on either theme
SPOTIFY_TEXT = "#FFFFFF"
SPOTIFY_MUTED = "#B3B3B3"


def spotify_card(track, t):
    """A track card with a looping equaliser.

    GitHub strips <iframe>, so Spotify's own embed player can never render in a
    README. This is drawn from the public oEmbed data instead — real cover art,
    title and artist — and the bars animate through SMIL, which does survive the
    image proxy.

    Deliberately not theme-split: GitHub rewrites a <picture> into its own
    <themed-picture> element, which drops the surrounding <a> and stretches the
    image to the full column. A single flat <img> keeps the card clickable and
    the right size, so it wears Spotify's dark palette in both themes.
    """
    W, H = 432, 96
    art = 68
    o = [f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" '
         f'fill="{SPOTIFY_BG}" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>']

    o.append(f'<clipPath id="c"><rect x="14" y="14" width="{art}" height="{art}" rx="8"/></clipPath>')
    o.append(f'<image x="14" y="14" width="{art}" height="{art}" href="{track["art"]}" '
             f'clip-path="url(#c)" preserveAspectRatio="xMidYMid slice"/>')

    title = track["title"]
    if len(title) > 24:
        title = title[:23].rstrip() + "\u2026"
    o.append(text(96, 39, title, size=15, fill=SPOTIFY_TEXT, weight=600))
    o.append(text(96, 57, track["artist"], size=12.5, fill=SPOTIFY_MUTED))
    o.append(f'<circle cx="99.5" cy="71" r="3.5" fill="{SPOTIFY_GREEN}"/>')
    o.append(text(109, 75, f'from {track["playlist"]}', size=10.5,
                  fill=SPOTIFY_MUTED, family=MONO))

    # Right-hand visualiser. SMIL is the only animation GitHub's image proxy
    # passes through, so the bars are keyframed rather than scripted.
    bars = [
        (10, 34, 14, 40, 12), (30, 12, 38, 18, 26), (18, 40, 10, 30, 16),
        (36, 16, 28, 12, 34), (12, 28, 40, 20, 10), (26, 38, 16, 34, 22),
        (40, 14, 24, 38, 18), (16, 30, 12, 26, 40), (22, 18, 36, 14, 28),
    ]
    base = 72
    for i, vals in enumerate(bars):
        x = 330 + i * 8.6
        hs = ",".join(str(v) for v in (*vals, vals[0]))
        ys = ",".join(str(base - v) for v in (*vals, vals[0]))
        o.append(
            f'<rect x="{x:.1f}" y="{base-vals[0]}" width="4.6" height="{vals[0]}" rx="2.3" '
            f'fill="{SPOTIFY_GREEN}" opacity="0.92">'
            f'<animate attributeName="height" values="{hs}" dur="1.6s" '
            f'begin="-{i*0.17:.2f}s" repeatCount="indefinite" calcMode="spline" '
            f'keySplines="0.4 0 0.6 1;0.4 0 0.6 1;0.4 0 0.6 1;0.4 0 0.6 1;0.4 0 0.6 1" '
            f'keyTimes="0;0.2;0.4;0.6;0.8;1"/>'
            f'<animate attributeName="y" values="{ys}" dur="1.6s" '
            f'begin="-{i*0.17:.2f}s" repeatCount="indefinite" calcMode="spline" '
            f'keySplines="0.4 0 0.6 1;0.4 0 0.6 1;0.4 0 0.6 1;0.4 0 0.6 1;0.4 0 0.6 1" '
            f'keyTimes="0;0.2;0.4;0.6;0.8;1"/></rect>')
    return svg(W, H, "\n".join(o))


def emit_spotify():
    data = json.loads((OUT / "spotify.json").read_text(encoding="utf-8"))
    for i, track in enumerate(data["tracks"], 1):
        (OUT / f"spotify-{i}.svg").write_text(
            spotify_card(track, None), encoding="utf-8")
    print(f"wrote {len(data['tracks'])} spotify cards")


def main():
    emit_tiles()
    emit_spotify()
    for name, fn in (("banner", banner), ("langs", langs),
                     ("activity", activity), ("clock", clock)):
        for mode, theme in THEMES.items():
            path = OUT / f"{name}-{mode}.svg"
            path.write_text(fn(theme, mode), encoding="utf-8")
            print(f"wrote {path.relative_to(OUT.parent)}")


if __name__ == "__main__":
    main()
