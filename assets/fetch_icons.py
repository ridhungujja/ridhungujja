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
    # No icon set carries these two. Both are square marks rather than tiles, so
    # they get a plate of their own to match the rest of the strip.
    "statsmodels": ("svgart", "https://www.statsmodels.org/stable/_images/"
                              "statsmodels-logo-v2-no-text.svg"),
    "Stata": ("raster", "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSH_"
                        "8xa4FdiSV7T03dHiaz5nCXYjsB0cfLe4d9el_12lST7wfSrpZW2LVQ&s=10"),
}

# Which ground a non-tile mark sits on. Matplotlib's is drawn in white and needs
# a dark plate; the other two are dark-inked and need a light one.
PLATES = {"Matplotlib": "#242938", "statsmodels": "#F4F2ED", "Stata": "#FFFFFF"}

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
    "?text=Pickleball%20%20%26%20Eats%3F%3F&emoji=%F0%9F%8C%AF&slug=ridhungujja"
    "&button_colour=225376&font_colour=ffffff&font_family=Lato"
    "&outline_colour=ffffff&coffee_colour=FFDD00"
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
    """Vendor the button with its supporter counter trimmed off.

    Everything here is measured from the fetched file rather than hardcoded:
    the button's width and the counter's offset both change with the label, so
    fixed numbers silently leave the heart behind and squash the artwork.
    """
    body = get(BMC_URL)
    if not body:
        print("  !! could not fetch the Buy Me a Coffee button")
        return

    # Their API drops the button text in raw, so an "&" in it lands unescaped and
    # the SVG stops being well-formed. Escaping bare ampersands keeps the literal
    # "&" on the button instead of forcing a reworded label.
    body = re.sub(r"&(?!#?\w+;)", "&amp;", body)

    full = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', body)
    width, height = (float(full.group(1)), float(full.group(2))) if full else (253.0, 50.0)

    # The counter lives in a translated group whose first path starts at the
    # divider; that x plus the group's offset is where the button really ends.
    crop = width
    g = re.search(r'<g transform="translate\(([\d.-]+),\s*[\d.-]+\)"\s*>', body)
    if g:
        start = g.start()
        end = body.find("</g>", start)
        inner = body[start:end]
        edge = re.search(r'\sd="M([\d.]+)', inner)
        if edge:
            crop = float(edge.group(1)) + float(g.group(1))
        body = body[:start] + body[end + 4:]

    # any leftover count sitting past the new edge
    body = re.sub(r'<text[^>]*\sx="([\d.]+)"[^>]*>.*?</text>',
                  lambda m: "" if float(m.group(1)) >= crop - 8 else m.group(0),
                  body, flags=re.S)

    crop = round(crop)
    body = re.sub(r'(<rect[^>]*?)width="[\d.]+"', rf'\g<1>width="{crop}"', body, count=1)
    body = body.replace(f'viewBox="0 0 {full.group(1)} {full.group(2)}"',
                        f'viewBox="0 0 {crop} {full.group(2)}"') if full else body
    body = re.sub(r'<svg\s', f'<svg width="{crop}" ', body, count=1)
    (ICON_DIR.parent / "bmc-button.svg").write_text(body, encoding="utf-8")
    print(f"  bmc-button.svg (counter trimmed, {crop}x{height:.0f})")


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
            manifest[label] = {"kind": "inset", "file": f"{slug}.svg",
                               "plate": PLATES.get(label, "#242938"), "same": True}

        elif source in ("svgart", "raster"):
            name = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
            if source == "svgart":
                body = get(slug)
                if not body:
                    print(f"  !! no artwork for {label}")
                    continue
                name += ".svg"
                (ICON_DIR / name).write_text(body, encoding="utf-8")
            else:
                try:
                    raw = urllib.request.urlopen(urllib.request.Request(
                        slug, headers={"User-Agent": "ridhungujja-profile-readme"}),
                        timeout=30).read()
                except (urllib.error.HTTPError, urllib.error.URLError):
                    print(f"  !! no artwork for {label}")
                    continue
                name += ".png"
                (ICON_DIR / name).write_bytes(raw)
            manifest[label] = {"kind": "inset", "file": name,
                               "plate": PLATES.get(label, "#F4F2ED"), "same": True}

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

# one track standing in for each playlist
TRACKS = [
    ("1zzejMGRYKP5XOa3FmzXfa", "0IUViMbUBPffUXQeDOyzDU"),  # southies
    ("7H7NyZ3G075GqPx2evsfeb", "0v23S8pWmoUcxv1chc8kzh"),  # cash curious
]


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
    out = {"tracks": []}
    for tid, plid in TRACKS:
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
        pl = get("https://open.spotify.com/oembed?url="
                 f"https://open.spotify.com/playlist/{plid}")
        out["tracks"].append({
            "id": tid,
            "title": title,
            "artist": _artist(tid),
            "playlist": json.loads(pl)["title"] if pl else "",
            "playlist_id": plid,
            "art": "data:image/jpeg;base64," + base64.b64encode(art).decode(),
        })
        t = out["tracks"][-1]
        print(f"  {t['title']} / {t['artist']} / from {t['playlist']}")

    (ICON_DIR.parent / "spotify.json").write_text(json.dumps(out), encoding="utf-8")


if __name__ == "__main__":
    main()
