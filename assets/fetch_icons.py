"""Download and cache the logo artwork used by the README tiles.

Everything is vendored into assets/icons/ so the published SVGs stay
self-contained: GitHub proxies README images, and a figure that hot-linked a
dozen CDNs would break the moment any one of them moved.

    python3 assets/fetch_icons.py

Sources, in order of preference:
  skill    tandpfun/skill-icons — a complete square tile, background included
  simple   simple-icons — a monochrome glyph we set on the brand colour
  devicon  devicons/devicon — colour artwork that needs its own background
  wordmark the vendor's own horizontal logo, for tools no icon set carries
"""

import base64
import json
import re
import urllib.error
import urllib.request
from pathlib import Path

ICON_DIR = Path(__file__).parent / "icons"
SKILL = "https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/{}.svg"
SIMPLE = "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/{}.svg"
DEVICON = "https://raw.githubusercontent.com/devicons/devicon/master/icons/{0}/{0}-original.svg"

ICONS = {
    # languages
    "Python": ("skill", "Python"),
    "R": ("skill", "R"),
    "SQL": ("skill", "PostgreSQL"),
    "LaTeX": ("skill", "LaTeX"),
    "JavaScript": ("skill", "JavaScript"),
    "HTML": ("skill", "HTML"),
    "CSS": ("skill", "CSS"),
    "Bash": ("skill", "Bash"),
    # libraries
    "pandas": ("simple", "pandas"),
    "NumPy": ("simple", "numpy"),
    "SciPy": ("simple", "scipy"),
    "Matplotlib": ("devicon", "matplotlib"),
    "React": ("skill", "React"),
    "Next.js": ("skill", "NextJS"),
    # tools
    "Git": ("skill", "Git"),
    "GitHub": ("skill", "Github"),
    "Claude Code": ("simple", "claude"),
    "pytest": ("simple", "pytest"),
    # socials
    "Gmail": ("skill", "Gmail"),
    "LinkedIn": ("skill", "LinkedIn"),
    "Instagram": ("skill", "Instagram"),
    "Spotify": ("skill", "Spotify"),
    # No icon set carries these two, so we take the vendor's own wordmark. Both
    # are dark-inked, so they sit on a light plate in either theme.
    # pdfplumber has no logo anywhere and stays a text plate.
    "statsmodels": ("wordmark", "https://raw.githubusercontent.com/statsmodels/"
                                "statsmodels/main/docs/source/images/"
                                "statsmodels-logo-v2-horizontal.svg"),
    "Stata": ("wordmark", "https://www.stata.com/includes/images/stata-logo-blue.svg"),
}

# skill-icons artwork already ships its own tile background. The monochrome
# simple-icons glyphs don't, so each gets its brand colour behind a white mark —
# the same treatment skill-icons gives Git or Bash.
BRAND = {
    "pandas": "#150458",
    "numpy": "#4DABCF",
    "scipy": "#8CAAE6",
    "pytest": "#0A9EDC",
    "claude": "#D97757",
}

# Buy Me a Coffee's button API always bakes a supporter counter into the right
# edge of the SVG, and there is no parameter to turn it off. The counter is an
# overlay group starting at x=200.8, so vendoring the button and trimming to
# x=200 gives the plain button — the same thing their <script> widget renders,
# which a README can't run because GitHub strips JavaScript.
BMC_URL = (
    "https://img.buymeacoffee.com/button-api/"
    "?text=Pickleball%20%2B%20Eats&emoji=%F0%9F%8C%AF&slug=ridhungujja"
    "&button_colour=FF5F5F&font_colour=ffffff&font_family=Bree"
    "&outline_colour=000000&coffee_colour=FFDD00"
)
BMC_CROP = 200


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "ridhungujja-profile-readme"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode("utf-8")
    except (urllib.error.HTTPError, urllib.error.URLError):
        return None


def fetch_bmc():
    body = get(BMC_URL)
    if not body:
        print("  !! could not fetch the Buy Me a Coffee button")
        return
    start = body.find('<g transform="translate(1,0)">')
    if start != -1:
        end = body.find("</g>", start)
        body = body[:start] + body[end + 4:]
    body = re.sub(r'<text[^>]*\sx="2\d\d"[^>]*>.*?</text>', "", body, flags=re.S)
    body = body.replace('width="253"', f'width="{BMC_CROP}"', 1)
    body = body.replace('viewBox="0 0 253 50"', f'viewBox="0 0 {BMC_CROP} 50"')
    body = body.replace('<svg height="50"', f'<svg height="50" width="{BMC_CROP}"', 1)
    (ICON_DIR.parent / "bmc-button.svg").write_text(body, encoding="utf-8")
    print("  bmc-button.svg (counter trimmed)")


def main():
    ICON_DIR.mkdir(exist_ok=True)
    manifest = {}

    for label, (source, slug) in ICONS.items():
        if source == "skill":
            variants = {}
            for mode in ("light", "dark"):
                body = get(SKILL.format(f"{slug}-{mode.capitalize()}"))
                if body:
                    variants[mode] = body
            if not variants:
                body = get(SKILL.format(slug))
                if not body:
                    print(f"  !! no artwork for {label}")
                    continue
                variants = {"light": body, "dark": body}
            variants.setdefault("dark", variants["light"])
            variants.setdefault("light", variants["dark"])
            for mode, body in variants.items():
                (ICON_DIR / f"{slug}-{mode}.svg").write_text(body, encoding="utf-8")
            manifest[label] = {
                "kind": "tile",
                "light": f"{slug}-light.svg",
                "dark": f"{slug}-dark.svg",
                "same": variants["light"] == variants["dark"],
            }

        elif source == "devicon":
            body = get(DEVICON.format(slug))
            if not body:
                print(f"  !! no artwork for {label}")
                continue
            (ICON_DIR / f"{slug}.svg").write_text(body, encoding="utf-8")
            manifest[label] = {"kind": "inset", "light": f"{slug}.svg",
                               "dark": f"{slug}.svg", "same": True}

        elif source == "wordmark":
            body = get(slug)
            if not body:
                print(f"  !! no wordmark for {label}")
                continue
            name = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-") + "-wordmark.svg"
            (ICON_DIR / name).write_text(body, encoding="utf-8")
            box = re.search(r'viewBox="([^"]+)"', body)
            manifest[label] = {
                "kind": "wordmark",
                "file": name,
                "viewBox": box.group(1) if box else "0 0 100 24",
                "same": True,
            }

        else:  # simple-icons
            body = get(SIMPLE.format(slug))
            if not body:
                print(f"  !! no artwork for {label}")
                continue
            paths = re.findall(r'<path[^>]*\sd="([^"]+)"', body)
            box = re.search(r'viewBox="([^"]+)"', body)
            if not paths:
                print(f"  !! no path in {label}")
                continue
            manifest[label] = {
                "kind": "glyph",
                "d": " ".join(paths),
                "viewBox": box.group(1) if box else "0 0 24 24",
                "brand": BRAND.get(slug, "#475569"),
                "same": True,
            }
        print(f"  {label:<14} {source}")

    fetch_bmc()
    fetch_spotify()
    (ICON_DIR / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print(f"\n{len(manifest)} icons cached in {ICON_DIR.name}/")




# ---------------------------------------------------------------------------
# Spotify
#
# A genuinely live "now playing" needs an OAuth client secret and refresh
# token, which belong to the account owner and must never be handled here. The
# oEmbed endpoint is public and unauthenticated, so the cards below carry real
# titles, artists and cover art without any credential at all.
# ---------------------------------------------------------------------------

TRACKS = ["1zzejMGRYKP5XOa3FmzXfa", "7H7NyZ3G075GqPx2evsfeb"]
PLAYLIST = "0v23S8pWmoUcxv1chc8kzh"


def _artist(track_id):
    page = get(f"https://open.spotify.com/embed/track/{track_id}")
    if not page:
        return ""
    m = re.search(r'"artists":(\[.*?\])', page)
    if not m:
        return ""
    try:
        return ", ".join(a["name"] for a in json.loads(m.group(1)))
    except (ValueError, KeyError):
        return ""


def fetch_spotify():
    out = {"tracks": [], "playlist": {}}
    for tid in TRACKS:
        meta = get(f"https://open.spotify.com/oembed?url=https://open.spotify.com/track/{tid}")
        if not meta:
            print(f"  !! no Spotify metadata for {tid}")
            continue
        meta = json.loads(meta)
        art = urllib.request.urlopen(
            urllib.request.Request(meta["thumbnail_url"],
                                   headers={"User-Agent": "ridhungujja-profile-readme"}),
            timeout=30).read()
        title = re.split(r"\s+-\s+From\b", meta["title"])[0].strip()
        out["tracks"].append({
            "id": tid,
            "title": title,
            "artist": _artist(tid),
            "art": "data:image/jpeg;base64," + base64.b64encode(art).decode(),
        })
        print(f"  {title} — {out['tracks'][-1]['artist']}")

    pl = get(f"https://open.spotify.com/oembed?url=https://open.spotify.com/playlist/{PLAYLIST}")
    if pl:
        out["playlist"] = {"id": PLAYLIST, "title": json.loads(pl)["title"]}
        print(f"  playlist: {out['playlist']['title']}")

    (ICON_DIR.parent / "spotify.json").write_text(json.dumps(out), encoding="utf-8")


if __name__ == "__main__":
    main()
