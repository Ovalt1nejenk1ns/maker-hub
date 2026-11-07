"""Fetch fresh data -> data/feed.json and append star snapshots to data/history.csv.

Uses only the standard library. Set GITHUB_TOKEN to raise the API rate limit
(GitHub Actions provides one automatically).
"""
import csv, json, os, sys, urllib.parse, urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "maker-hub-collector"})
    token = os.environ.get("GITHUB_TOKEN")
    if token and "api.github.com" in url:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def github_repos(topic_cfg, since):
    seen, repos = set(), []
    for q in topic_cfg["github_queries"]:
        params = urllib.parse.urlencode(
            {"q": q.format(since=since), "sort": "stars", "order": "desc", "per_page": 10})
        try:
            items = get_json(f"https://api.github.com/search/repositories?{params}")["items"]
        except Exception as e:  # one failed query shouldn't kill the run
            print(f"  github query failed ({q}): {e}", file=sys.stderr)
            continue
        for it in items:
            if it["full_name"] in seen or it.get("archived"):
                continue
            seen.add(it["full_name"])
            repos.append({
                "name": it["full_name"],
                "url": it["html_url"],
                "desc": (it["description"] or "").strip(),
                "language": it["language"] or "—",
                "stars": it["stargazers_count"],
                "created": it["created_at"][:10],
                "pushed": it["pushed_at"][:10],
            })
    repos.sort(key=lambda r: r["stars"], reverse=True)
    return repos[: config.ITEMS_PER_TOPIC]


def hn_stories(query, since_ts):
    params = urllib.parse.urlencode({
        "query": query, "tags": "story", "hitsPerPage": 5,
        "numericFilters": f"created_at_i>{since_ts},points>5"})
    try:
        hits = get_json(f"https://hn.algolia.com/api/v1/search?{params}")["hits"]
    except Exception as e:
        print(f"  hn query failed ({query}): {e}", file=sys.stderr)
        return None  # None = "couldn't fetch", so build keeps the old value
    return [{
        "title": h["title"], "points": h["points"],
        "url": h.get("url") or f"https://news.ycombinator.com/item?id={h['objectID']}",
        "hn_url": f"https://news.ycombinator.com/item?id={h['objectID']}",
    } for h in sorted(hits, key=lambda h: h["points"], reverse=True)]


def main():
    today = date.today()
    since = (today - timedelta(days=config.LOOKBACK_DAYS)).isoformat()
    since_ts = int((datetime.now(timezone.utc) - timedelta(days=14)).timestamp())

    old = {}
    feed_path = DATA / "feed.json"
    if feed_path.exists():
        old = json.loads(feed_path.read_text())

    feed = {"updated": today.isoformat(), "topics": {}}
    snapshots = []
    for key, cfg in config.TOPICS.items():
        print(f"{key}…")
        repos = github_repos(cfg, since)
        hn = hn_stories(cfg["hn_query"], since_ts)
        prev = old.get("topics", {}).get(key, {})
        feed["topics"][key] = {
            "repos": repos or prev.get("repos", []),   # keep last good data on failure
            "hn": hn if hn is not None else prev.get("hn", []),
        }
        snapshots += [(today.isoformat(), key, r["name"], r["stars"]) for r in repos]

    feed_path.write_text(json.dumps(feed, indent=2, ensure_ascii=False))

    # history.csv: one row per (date, repo). Re-running the same day replaces that day's rows.
    hist = DATA / "history.csv"
    rows = []
    if hist.exists():
        with hist.open() as f:
            rows = [r for r in csv.reader(f)][1:]
    rows = [r for r in rows if r[0] != today.isoformat()] + [list(map(str, s)) for s in snapshots]
    with hist.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "topic", "repo", "stars"])
        w.writerows(rows)
    print(f"wrote {len(snapshots)} snapshots")


if __name__ == "__main__":
    main()
