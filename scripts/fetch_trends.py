"""
fetch_trends.py
Pulls trending content from GitHub, Reddit, and Hacker News.
Saves results to trends_data.json for use by refresh_hub.py.
"""

import json
import time
import requests
from datetime import datetime, timedelta, timezone

HEADERS = {
    "User-Agent": "maker-hub-refresh/1.0 (github.com/Ovalt1nejenk1ns/maker-hub)"
}


# ── GitHub ────────────────────────────────────────────────────────────────────

def fetch_github_trending(topics, days=14):
    """
    Use the GitHub Search API to find top-starred repos active in the
    last `days` days for each maker-relevant topic.
    No auth required; rate-limited to 10 req/min unauthenticated.
    """
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    results = []
    seen = set()

    for topic in topics:
        url = (
            f"https://api.github.com/search/repositories"
            f"?q=topic:{topic}+pushed:>{since}"
            f"&sort=stars&order=desc&per_page=5"
        )
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            r.raise_for_status()
            for item in r.json().get("items", []):
                name = item["full_name"]
                if name not in seen:
                    seen.add(name)
                    results.append({
                        "name": name,
                        "description": item.get("description") or "",
                        "stars": item["stargazers_count"],
                        "url": item["html_url"],
                        "topic": topic,
                    })
        except Exception as e:
            print(f"  [GitHub] Error fetching topic '{topic}': {e}")

        time.sleep(0.5)   # stay well under rate limit

    # Sort by stars, cap at 12
    results.sort(key=lambda x: x["stars"], reverse=True)
    return results[:12]


# ── Reddit ────────────────────────────────────────────────────────────────────

def fetch_reddit_top(subreddits, limit=5):
    """
    Fetch top posts from the past week across maker/data subreddits.
    Uses Reddit's public JSON API — no auth needed.
    """
    results = []

    for sub in subreddits:
        url = f"https://www.reddit.com/r/{sub}/top.json?t=week&limit={limit}"
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            r.raise_for_status()
            posts = r.json().get("data", {}).get("children", [])
            for post in posts:
                d = post["data"]
                if d.get("stickied") or d.get("score", 0) < 50:
                    continue
                results.append({
                    "title": d["title"],
                    "subreddit": sub,
                    "score": d["score"],
                    "comments": d.get("num_comments", 0),
                    "url": f"https://reddit.com{d['permalink']}",
                })
        except Exception as e:
            print(f"  [Reddit] Error fetching r/{sub}: {e}")

        time.sleep(0.3)

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:12]


# ── Hacker News ───────────────────────────────────────────────────────────────

MAKER_KEYWORDS = [
    "python", "arduino", "esp32", "robotics", "embedded",
    "raspberry pi", "data", "machine learning", "ai", "rust",
    "maker", "3d print", "microcontroller", "iot", "homelab",
    "automation", "open source hardware",
]

def fetch_hn_top(limit=8):
    """
    Fetch top HN stories filtered to maker/data/engineering topics.
    Uses the official Firebase-backed HN API.
    """
    try:
        r = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            timeout=10,
        )
        story_ids = r.json()[:150]
    except Exception as e:
        print(f"  [HN] Could not fetch top story list: {e}")
        return []

    stories = []
    for sid in story_ids:
        if len(stories) >= limit:
            break
        try:
            r = requests.get(
                f"https://hacker-news.firebaseio.com/v0/item/{sid}.json",
                timeout=5,
            )
            item = r.json()
            if not item or item.get("type") != "story" or not item.get("title"):
                continue
            title_lower = item["title"].lower()
            if any(kw in title_lower for kw in MAKER_KEYWORDS):
                stories.append({
                    "title": item["title"],
                    "url": item.get("url") or f"https://news.ycombinator.com/item?id={sid}",
                    "score": item.get("score", 0),
                    "comments": item.get("descendants", 0),
                })
        except Exception:
            continue

    return stories


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    today = datetime.now().strftime("%B %d, %Y")

    print("Fetching GitHub trending repos...")
    github = fetch_github_trending([
        "python", "arduino", "esp32", "robotics", "data-analytics",
        "raspberry-pi", "machine-learning", "home-automation",
    ])
    print(f"  → {len(github)} repos")

    print("Fetching Reddit top posts...")
    reddit = fetch_reddit_top([
        "arduino", "esp32", "learnpython", "robotics",
        "datascience", "homelab", "raspberry_pi", "MachineLearning",
    ])
    print(f"  → {len(reddit)} posts")

    print("Fetching Hacker News stories...")
    hn = fetch_hn_top(limit=8)
    print(f"  → {len(hn)} stories")

    data = {
        "fetched_at": today,
        "github_trending": github,
        "reddit_top": reddit,
        "hn_top": hn,
    }

    with open("trends_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"\nSaved trends_data.json ({len(github)} GH repos · {len(reddit)} Reddit · {len(hn)} HN)")
