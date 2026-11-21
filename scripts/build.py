"""data/*.json|csv + content/ + templates/ -> site/ (plain static HTML). Run: python scripts/build.py"""
import csv, json, shutil, sys
from urllib.parse import quote, urlencode
import markdown
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import config
from charts import bar_chart, line_chart

SITE = ROOT / "site"
env = Environment(loader=FileSystemLoader(ROOT / "templates"),
                  autoescape=select_autoescape(["html"]))


def pin_url(title="", url="", topic="", kind="Link"):
    """Link that opens a pre-filled 'new issue' form; submitting it pins the item to the board."""
    body = (f"url: {url}\ntopic: {topic}\nkind: {kind}\n\n"
            "<!-- Optional: write a note below about why you saved this. Close this issue to unpin. -->\n")
    q = urlencode({"labels": config.PIN_LABEL, "title": title, "body": body}, quote_via=quote)
    return f"https://github.com/{config.GITHUB_REPO}/issues/new?{q}"


# Bookmarklet: pin whatever page you're on (any site) with one click from the bookmarks bar.
def bookmarklet():
    base = f"https://github.com/{config.GITHUB_REPO}/issues/new?labels={config.PIN_LABEL}"
    return ("javascript:(()=>{const b='url: '+location.href+'\\ntopic: \\nkind: Article\\n\\n';"
            f"window.open('{base}&title='+encodeURIComponent(document.title)"
            "+'&body='+encodeURIComponent(b))})()")


env.globals["pin_url"] = pin_url


def render(name, out, root, **ctx):
    path = SITE / out
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(env.get_template(name).render(
        root=root, cfg=config, topics=config.TOPICS, **ctx), encoding="utf-8")


def load_json(rel, default):
    p = ROOT / rel
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def md(rel):
    return md_toc(rel)[0]


def md_toc(rel, level=2):
    """Markdown -> (html, [(anchor_id, heading_text), ...]) for headings at `level`.

    The 'toc' extension adds id="..." to every heading, so the list can drive
    jump links on the cheat-sheet sidebar and the home page's reference tiles.
    """
    p = ROOT / rel
    if not p.exists():
        return "", []
    conv = markdown.Markdown(extensions=["tables", "fenced_code", "toc"])
    html = conv.convert(p.read_text(encoding="utf-8"))

    def walk(tokens):
        for t in tokens:
            if t["level"] == level:
                yield t["id"], t["name"]
            yield from walk(t["children"])
    return html, list(walk(conv.toc_tokens))


def momentum(repos, hist_topic, updated):
    """Rank repos by stars gained between the two most recent snapshots (newest tools float up).

    Adds 'gain' (int or None if not enough history) and 'fresh' (created in the last year).
    Total stars only break ties, so a 10-year-old giant no longer outranks a hot new tool.
    """
    dates = sorted({d for pts in hist_topic.values() for d, _ in pts})
    prev, last = (dates[-2], dates[-1]) if len(dates) >= 2 else (None, None)
    year_ago = f"{int(updated[:4]) - 1}{updated[4:]}"
    out = []
    for r in repos:
        by_date = dict(hist_topic.get(r["name"], []))
        gain = by_date[last] - by_date[prev] if prev and prev in by_date and last in by_date else None
        out.append(dict(r, gain=gain, fresh=r.get("created", "") >= year_ago))
    out.sort(key=lambda r: (r["gain"] if r["gain"] is not None else -1, r["stars"]), reverse=True)
    return out, prev


PER_WEEK = 5                                   # ideas / rabbit holes shown per topic page
LEVELS = {"Beginner": 0, "Intermediate": 1, "Advanced": 2}


def this_week(items, n=PER_WEEK, today=None):
    """Pick this week's n items from a larger pool, in file order, wrapping round at the end.

    The pick changes each Saturday (UTC), in step with the Friday-night refresh, so every
    build during the same week shows the same items.
    """
    if len(items) <= n:
        return items
    week = ((today or date.today()).toordinal() - 6) // 7      # ordinal % 7 == 6 is a Saturday
    start = (week * n) % len(items)
    return [items[(start + j) % len(items)] for j in range(n)]


def build_digest(feed, hist):
    """'This week' strip for the home page: star gainers, fresh news, top HN stories."""
    dates = sorted({d for repos in hist.values() for pts in repos.values() for d, _ in pts})
    gainers, since = [], ""
    if len(dates) >= 2:
        latest, since = dates[-1], dates[-2]
        for key, repos in hist.items():
            if key not in config.TOPICS:
                continue
            for name, pts in repos.items():
                by_date = dict(pts)                      # one value per date, last wins
                if latest in by_date and since in by_date:
                    gain = by_date[latest] - by_date[since]
                    if gain > 0:
                        gainers.append({"name": name, "topic": key, "gain": gain,
                                        "stars": by_date[latest],
                                        "url": f"https://github.com/{name}"})
        gainers.sort(key=lambda g: g["gain"], reverse=True)

    news, seen, per_topic = [], set(), Counter()
    all_news = [dict(n, topic=k) for k in config.TOPICS for n in feed["topics"][k].get("news", [])]
    for n in sorted(all_news, key=lambda n: n.get("date", ""), reverse=True):
        if n["url"] in seen or per_topic[n["topic"]] >= 3:   # at most 3 per topic
            continue
        seen.add(n["url"]); per_topic[n["topic"]] += 1
        news.append(n)

    hn, seen = [], set()
    all_hn = [dict(s, topic=k) for k in config.TOPICS for s in feed["topics"][k].get("hn", [])]
    for s in sorted(all_hn, key=lambda s: s["points"], reverse=True):
        if s["hn_url"] not in seen:
            seen.add(s["hn_url"]); hn.append(s)

    return {"gainers": gainers[:6], "since": since, "news": news[:10], "hn": hn[:5]}


def main():
    feed = json.loads((ROOT / "data/feed.json").read_text(encoding="utf-8"))
    hist = defaultdict(lambda: defaultdict(list))  # topic -> repo -> [(date, stars)]
    hp = ROOT / "data/history.csv"
    if hp.exists():
        with hp.open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                hist[r["topic"]][r["repo"]].append((r["date"], int(r["stars"])))

    if SITE.exists():
        shutil.rmtree(SITE)
    shutil.copytree(ROOT / "static", SITE)

    all_tips = load_json("content/tips.json", {})
    label = {k: f'{c["icon"]} {c["label"]}' for k, c in config.TOPICS.items()}
    site_tips = [{"t": t, "s": label[k]} for k in config.TOPICS for t in all_tips.get(k, [])]
    pins = load_json("data/pins.json", [])
    common = dict(updated=feed["updated"], page_tips=site_tips, n_pins=len(pins))
    search = []      # site-wide search index: t=title, u=url, k=kind, s=topic
    home_ideas, home_holes = [], []
    reference, fresh_tools, seen_tools = [], [], set()

    def add(title, url, kind, key):
        if title and url:
            search.append({"t": title, "u": url, "k": kind, "s": label[key]})

    for key, cfg in config.TOPICS.items():
        t = feed["topics"][key]
        resources = load_json(f"data/resources/{key}.json", [])
        ideas_pool = load_json(f"content/ideas/{key}.json", [])
        holes_pool = load_json(f"content/adjacent/{key}.json", [])
        ideas = sorted(this_week(ideas_pool), key=lambda i: LEVELS.get(i["level"], 1))
        adjacent = this_week(holes_pool)
        sheet_html, sheet_toc = md_toc(f"content/cheatsheets/{key}.md")
        has_sheet = bool(sheet_html)
        quickref, quickref_toc = md_toc(f"content/quickref/{key}.md", level=3)
        radar, radar_since = momentum(t["repos"], hist[key], feed["updated"])
        reference.append({"key": key, "toc": sheet_toc, "has_sheet": has_sheet,
                          "quickref": bool(quickref), "resources": sum(len(g["items"]) for g in resources)})
        for r in radar:
            if r["fresh"] and r["name"] not in seen_tools:
                seen_tools.add(r["name"]); fresh_tools.append(dict(r, topic=key))
        tips = [{"t": x, "s": label[key]} for x in all_tips.get(key, [])]
        render("topic.html", f"{key}/index.html", "../", key=key, t=t, tcfg=cfg,
               resources=resources, has_sheet=has_sheet, quickref=quickref,
               quickref_toc=quickref_toc, sheet_toc=sheet_toc, radar=radar, radar_since=radar_since,
               ideas=ideas, adjacent=adjacent, ideas_total=len(ideas_pool),
               holes_total=len(holes_pool), **{**common, "page_tips": tips or site_tips})
        if has_sheet:
            render("cheatsheet.html", f"{key}/cheatsheet/index.html", "../../",
                   key=key, tcfg=cfg, body=sheet_html, toc=sheet_toc,
                   **{**common, "page_tips": tips or site_tips})
            add(f'{cfg["label"]} cheat sheet', f"{key}/cheatsheet/index.html", "Cheat sheet", key)

        add(cfg["label"], f"{key}/index.html", "Topic", key)
        for n in t.get("news", []):
            add(n["title"], n["url"], "News", key)
        for r in t.get("repos", []):
            add(f'{r["name"]}: {r.get("desc") or ""}'.rstrip(": "), r["url"], "Repo", key)
        for s in t.get("hn", []):
            add(s["title"], s["url"], "Hacker News", key)
        for g in resources:
            for r in g["items"]:
                add(f'{r["title"]}: {r.get("note", "")}'.rstrip(": "), r["url"], "Resource", key)
        for i, idea in enumerate(ideas, 1):
            url = f"{key}/index.html#idea-{i}"
            add(f'{idea["title"]}: {idea["desc"]}', url, "Project idea", key)
            home_ideas.append({"t": idea["title"], "d": idea["desc"], "s": label[key], "u": url,
                               "m": f'{idea["level"]} · {idea["time"]}'})
        for a in holes_pool:
            add(f'{a["title"]}: {a["why"]}', a["url"], "Rabbit hole", key)
            home_holes.append({"t": a["title"], "d": a["why"], "u": a["url"],
                               "s": f"Next door to {label[key]}", "m": a.get("how", "")})

    fresh_tools.sort(key=lambda r: (r["gain"] or 0, r["stars"]), reverse=True)
    render("index.html", "index.html", "", feed=feed, digest=build_digest(feed, hist),
           reference=reference, fresh_tools=fresh_tools[:6],
           home_ideas=home_ideas, home_holes=home_holes, **common)

    dash = {}
    for key, cfg in config.TOPICS.items():
        repos = feed["topics"][key]["repos"]
        langs = Counter(r["language"] for r in repos if r["language"] != "—")
        # repos with >=2 snapshots can be drawn as a trend line
        tracked = {n: p for n, p in hist[key].items() if len(p) >= 2}
        top = sorted(tracked, key=lambda n: tracked[n][-1][1], reverse=True)[:6]
        dash[key] = {
            "bars": bar_chart([(r["name"], r["stars"]) for r in repos]),
            "langs": bar_chart(langs.most_common(6)),
            "trend": line_chart({n: tracked[n] for n in top}),
            "snapshots": len({d for p in hist[key].values() for d, _ in p}),
            "legend": top,
        }
    render("dashboards.html", "dashboards/index.html", "../", dash=dash, **common)
    render("board.html", "board/index.html", "../", pins=pins, active="board",
           bookmarklet=bookmarklet(), **common)
    for pin in pins:
        add(pin["title"], pin["url"], "Pinned", pin["topic"]) if pin["topic"] else \
            search.append({"t": pin["title"], "u": pin["url"], "k": "Pinned", "s": "📌 Board"})
    add_dash = {"t": "Dashboards: star charts and trends", "u": "dashboards/index.html", "k": "Page", "s": "📊 Dashboards"}
    (SITE / "search.json").write_text(json.dumps(search + [add_dash], ensure_ascii=False), encoding="utf-8")
    print(f"built {sum(1 for _ in SITE.rglob('*.html'))} pages, {len(search) + 1} search entries -> {SITE}")


if __name__ == "__main__":
    main()
