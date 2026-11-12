"""data/*.json|csv + content/ + templates/ -> site/ (plain static HTML). Run: python scripts/build.py"""
import csv, json, shutil, sys
import markdown
from collections import Counter, defaultdict
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


def render(name, out, root, **ctx):
    path = SITE / out
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(env.get_template(name).render(
        root=root, cfg=config, topics=config.TOPICS, **ctx), encoding="utf-8")


def load_json(rel, default):
    p = ROOT / rel
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def md(rel):
    p = ROOT / rel
    return (markdown.markdown(p.read_text(encoding="utf-8"), extensions=["tables", "fenced_code"])
            if p.exists() else "")


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
        if n["url"] in seen or per_topic[n["topic"]] >= 2:   # at most 2 per topic
            continue
        seen.add(n["url"]); per_topic[n["topic"]] += 1
        news.append(n)

    hn, seen = [], set()
    all_hn = [dict(s, topic=k) for k in config.TOPICS for s in feed["topics"][k].get("hn", [])]
    for s in sorted(all_hn, key=lambda s: s["points"], reverse=True):
        if s["hn_url"] not in seen:
            seen.add(s["hn_url"]); hn.append(s)

    return {"gainers": gainers[:6], "since": since, "news": news[:6], "hn": hn[:4]}


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
    common = dict(updated=feed["updated"], page_tips=site_tips)
    search = []      # site-wide search index: t=title, u=url, k=kind, s=topic
    home_ideas, home_holes = [], []

    def add(title, url, kind, key):
        if title and url:
            search.append({"t": title, "u": url, "k": kind, "s": label[key]})

    for key, cfg in config.TOPICS.items():
        t = feed["topics"][key]
        resources = load_json(f"data/resources/{key}.json", [])
        ideas = load_json(f"content/ideas/{key}.json", [])
        adjacent = load_json(f"content/adjacent/{key}.json", [])
        has_sheet = (ROOT / f"content/cheatsheets/{key}.md").exists()
        quickref = md(f"content/quickref/{key}.md")
        tips = [{"t": x, "s": label[key]} for x in all_tips.get(key, [])]
        render("topic.html", f"{key}/index.html", "../", key=key, t=t, tcfg=cfg,
               resources=resources, has_sheet=has_sheet, quickref=quickref,
               ideas=ideas, adjacent=adjacent, **{**common, "page_tips": tips or site_tips})
        if has_sheet:
            render("cheatsheet.html", f"{key}/cheatsheet/index.html", "../../",
                   key=key, tcfg=cfg, body=md(f"content/cheatsheets/{key}.md"),
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
        for a in adjacent:
            add(f'{a["title"]}: {a["why"]}', a["url"], "Rabbit hole", key)
            home_holes.append({"t": a["title"], "d": a["why"], "u": a["url"],
                               "s": f"Next door to {label[key]}", "m": a.get("how", "")})

    render("index.html", "index.html", "", feed=feed, digest=build_digest(feed, hist),
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
    add_dash = {"t": "Dashboards: star charts and trends", "u": "dashboards/index.html", "k": "Page", "s": "📊 Dashboards"}
    (SITE / "search.json").write_text(json.dumps(search + [add_dash], ensure_ascii=False), encoding="utf-8")
    print(f"built {sum(1 for _ in SITE.rglob('*.html'))} pages, {len(search) + 1} search entries -> {SITE}")


if __name__ == "__main__":
    main()
