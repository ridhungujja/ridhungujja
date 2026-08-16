"""Pull the numbers the README figures are drawn from into assets/data.json.

Uses the `gh` CLI when it is available, otherwise a GITHUB_TOKEN from the
environment. Run make_assets.py afterwards to redraw the SVGs.

    python3 assets/fetch_data.py && python3 assets/make_assets.py
"""

import json
import os
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

USER = "ridhungujja"
OUT = Path(__file__).parent / "data.json"

# Iterations of a project that already appears under another name. Counting all
# three podium repos would triple-count the same TypeScript.
EXCLUDE = {"podium.2", "podium-1.0"}

QUERY = """
query($login: String!) {
  user(login: $login) {
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
      totalCount
      nodes {
        name
        stargazerCount
        languages(first: 20, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection {
      totalCommitContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount weekday } }
      }
    }
  }
}
"""


def run_query():
    payload = {"query": QUERY, "variables": {"login": USER}}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        try:
            token = subprocess.run(
                ["gh", "auth", "token"], capture_output=True, text=True, check=True
            ).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            raise SystemExit("need a GITHUB_TOKEN in the environment or an authenticated gh CLI")

    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": f"{USER}-profile-readme",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = json.load(r)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"github api returned {e.code}: {e.read().decode()[:200]}")

    if "errors" in body:
        raise SystemExit(f"graphql errors: {body['errors']}")
    return body["data"]["user"]


def main():
    user = run_query()
    repos = [r for r in user["repositories"]["nodes"] if r["name"] not in EXCLUDE]

    totals, colors = {}, {}
    projects = 0
    for repo in repos:
        edges = repo["languages"]["edges"]
        if edges:
            projects += 1
        for e in edges:
            name = e["node"]["name"]
            totals[name] = totals.get(name, 0) + e["size"]
            colors[name] = e["node"]["color"] or "#8b949e"

    languages = [
        {"name": n, "bytes": b, "color": colors[n]}
        for n, b in sorted(totals.items(), key=lambda kv: -kv[1])
    ]

    cal = user["contributionsCollection"]["contributionCalendar"]
    weeks = [
        [{"date": d["date"], "count": d["contributionCount"], "weekday": d["weekday"]}
         for d in w["contributionDays"]]
        for w in cal["weeks"]
    ]

    data = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "languages": languages,
        "projects": projects,
        "stats": {
            "contributions": cal["totalContributions"],
            "commits": user["contributionsCollection"]["totalCommitContributions"],
            "repos": len(repos),
            "stars": sum(r["stargazerCount"] for r in repos),
            "bytes": sum(totals.values()),
        },
        "weeks": weeks,
    }
    OUT.write_text(json.dumps(data, indent=1), encoding="utf-8")
    print(f"wrote {OUT.name}: {data['stats']} across {projects} projects")


if __name__ == "__main__":
    main()
