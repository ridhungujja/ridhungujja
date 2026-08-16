"""Download and cache the logo artwork embedded in the stack figure.

Icons are vendored into assets/icons/ so the published SVGs stay self-contained:
GitHub proxies README images, and a figure that hot-linked a dozen CDNs would
break the moment any one of them moved. Re-run only when the stack changes.

    python3 assets/fetch_icons.py
"""

import json
import re
import urllib.error
import urllib.request
from pathlib import Path

ICON_DIR = Path(__file__).parent / "icons"
SKILL = "https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/{}.svg"
SIMPLE = "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/{}.svg"
DEVICON = "https://raw.githubusercontent.com/devicons/devicon/master/icons/{0}/{0}-original.svg"

# label -> (source, slug). "skill" art is full colour and ships a per-theme
# variant; "simple" and "devicon" are single files. statsmodels, Stata and
# pdfplumber have no logo in any of these sets and render as text-only chips.
ICONS = {
    "Python": ("skill", "Python"),
    "R": ("skill", "R"),
    "SQL": ("skill", "PostgreSQL"),
    "LaTeX": ("skill", "LaTeX"),
    "JavaScript": ("skill", "JavaScript"),
    "HTML": ("skill", "HTML"),
    "CSS": ("skill", "CSS"),
    "Bash": ("skill", "Bash"),
    "React": ("skill", "React"),
    "Next.js": ("skill", "NextJS"),
    "Git": ("skill", "Git"),
    "GitHub": ("skill", "Github"),
    "pandas": ("simple", "pandas"),
    "NumPy": ("simple", "numpy"),
    "SciPy": ("simple", "scipy"),
    "pytest": ("simple", "pytest"),
    "Claude Code": ("simple", "claude"),
    "Matplotlib": ("devicon", "matplotlib"),
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


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "ridhungujja-profile-readme"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode("utf-8")
    except urllib.error.HTTPError:
        return None


def main():
    ICON_DIR.mkdir(exist_ok=True)
    manifest = {}

    for label, (source, slug) in ICONS.items():
        if source == "skill":
            # Prefer the per-theme pair; several icons ship only one file.
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
                name = f"{slug}-{mode}.svg"
                (ICON_DIR / name).write_text(body, encoding="utf-8")
            manifest[label] = {"kind": "tile", "light": f"{slug}-light.svg",
                               "dark": f"{slug}-dark.svg"}

        elif source == "devicon":
            body = get(DEVICON.format(slug))
            if not body:
                print(f"  !! no artwork for {label}")
                continue
            (ICON_DIR / f"{slug}.svg").write_text(body, encoding="utf-8")
            manifest[label] = {"kind": "inset", "light": f"{slug}.svg", "dark": f"{slug}.svg"}

        else:  # simple-icons: monochrome, kept as a raw path we recolour per theme
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
            }
        print(f"  {label:<12} {source}")

    (ICON_DIR / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print(f"\n{len(manifest)} icons cached in {ICON_DIR.name}/")


if __name__ == "__main__":
    main()
