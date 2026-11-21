"""Nightly backup: copy the cloud scores database into this repo.

Writes two files:
  data/scorekeepers.json   every row, as readable JSON, so git shows exactly what changed
  data/scorekeepers.db     the same data as a SQLite file, ready for queries or DB Browser

Run: SCORES_API_URL=https://... SCORES_FAMILY_KEY=... python scorekeepers-cloud/backup.py
Standard library only. Exits with an error if the API can't be reached, so the
GitHub Action fails loudly instead of quietly skipping a night.
"""
import json
import os
import sqlite3
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"


def fetch_export(url: str, key: str) -> dict:
    req = urllib.request.Request(url.rstrip("/") + "/export",
                                 headers={"X-Family-Key": key, "User-Agent": "maker-hub-backup"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def write_db(export: dict, path: Path) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.unlink(missing_ok=True)
    conn = sqlite3.connect(tmp)
    try:
        conn.executescript((HERE / "schema.sql").read_text())   # same tables and view as the cloud
        for table in ("players", "games", "hands"):
            rows = export[table]
            if rows:
                cols = list(rows[0])
                conn.executemany(f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join('?' * len(cols))})",
                                 [tuple(r[c] for c in cols) for r in rows])
        conn.commit()
    finally:
        conn.close()
    tmp.replace(path)    # swap in only once it's complete, so a crash never leaves a half-written backup


def main() -> None:
    url, key = os.environ.get("SCORES_API_URL"), os.environ.get("SCORES_FAMILY_KEY")
    if not url or not key:
        sys.exit("Set SCORES_API_URL and SCORES_FAMILY_KEY")
    try:
        export = fetch_export(url, key)
    except Exception as e:
        sys.exit(f"Backup failed, could not read {url}/export: {e}")

    export.pop("exported_at", None)   # leave out the timestamp so an unchanged night makes no commit
    DATA.mkdir(exist_ok=True)
    (DATA / "scorekeepers.json").write_text(json.dumps(export, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    write_db(export, DATA / "scorekeepers.db")
    print(f"Backed up {len(export['games'])} games, {len(export['hands'])} hand rows, "
          f"{len(export['players'])} players")


if __name__ == "__main__":
    main()
