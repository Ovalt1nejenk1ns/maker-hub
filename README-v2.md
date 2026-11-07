# maker-hub (v2)

Static site built by Python. Topics: Python, 3D printing, woodworking.

    pip install -r requirements.txt
    python scripts/collect.py   # GitHub + HN APIs -> data/feed.json, data/history.csv
    python scripts/build.py     # data + templates -> site/
    python -m http.server -d site

- Add/remove a topic: edit `TOPICS` in `config.py`.
- Change look: `static/style.css` (colors are CSS variables at the top).
- Weekly refresh + deploy: `.github/workflows/refresh.yml` (repo Settings -> Pages -> Source: GitHub Actions).
- Trend charts need 2+ weekly snapshots in `data/history.csv`.
