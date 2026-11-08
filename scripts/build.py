"""data/*.json|csv + templates/ -> site/ (plain static HTML). Run: python scripts/build.py"""
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


def main():
    feed = json.loads((ROOT / "data/feed.json").read_text())
    hist = defaultdict(lambda: defaultdict(list))  # topic -> repo -> [(date, stars)]
    hp = ROOT / "data/history.csv"
    if hp.exists():
        with hp.open() as f:
            for r in csv.DictReader(f):
                hist[r["topic"]][r["repo"]].append((r["date"], int(r["stars"])))

    if SITE.exists():
        shutil.rmtree(SITE)
    shutil.copytree(ROOT / "static", SITE)

    common = dict(updated=feed["updated"])
    render("index.html", "index.html", "", feed=feed, **common)

    for key, cfg in config.TOPICS.items():
        t = feed["topics"][key]
        res_path = ROOT / f"data/resources/{key}.json"
        resources = json.loads(res_path.read_text()) if res_path.exists() else []
        sheet_path = ROOT / f"content/cheatsheets/{key}.md"
        has_sheet = sheet_path.exists()
        qr_path = ROOT / f"content/quickref/{key}.md"
        quickref = (markdown.markdown(qr_path.read_text(encoding="utf-8"),
                                      extensions=["tables", "fenced_code"])
                    if qr_path.exists() else "")
        render("topic.html", f"{key}/index.html", "../", key=key, t=t, tcfg=cfg,
               resources=resources, has_sheet=has_sheet, quickref=quickref, **common)
        if has_sheet:
            html = markdown.markdown(sheet_path.read_text(encoding="utf-8"),
                                     extensions=["tables", "fenced_code"])
            render("cheatsheet.html", f"{key}/cheatsheet/index.html", "../../",
                   key=key, tcfg=cfg, body=html, **common)

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
    print(f"built {sum(1 for _ in SITE.rglob('*.html'))} pages -> {SITE}")


if __name__ == "__main__":
    main()
