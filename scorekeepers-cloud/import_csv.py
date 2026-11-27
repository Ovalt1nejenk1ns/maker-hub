"""One-time import of an old league CSV (made by the Download CSV button) into the cloud.

    python scorekeepers-cloud/import_csv.py phase10 ../phase10-league/builder/game-1.csv --label "Game 1" --date 2026-11-20
    python scorekeepers-cloud/import_csv.py skipbo saturday.csv --label "Saturday night" --date 2026-11-21

Needs SCORES_API_URL and SCORES_FAMILY_KEY in the environment. Importing the same
file again replaces that game (its id comes from the game type and file name).
"""
import argparse
import csv
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

TRUE = {"TRUE", "YES", "Y", "1", "X"}


def read_rows(path: Path):
    settings, lines = {}, []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if line.startswith("#"):                          # Skip-Bo: "# target=500 stock=30"
            settings.update(p.split("=", 1) for p in line[1:].split() if "=" in p)
        elif line.strip():
            lines.append(line)
    return settings, list(csv.DictReader(lines))


def build_game(kind: str, path: Path, label: str, date: str) -> dict:
    settings, rows = read_rows(path)
    players, per_player = [], {}
    for r in rows:
        name = (r.get("Player") or "").strip()
        if not name:
            continue
        key = name.casefold()
        if key not in per_player:
            players.append(name.title() if kind == "phase10" else name)
            per_player[key] = []
        per_player[key].append(r)
    hands = []
    for k in range(len(next(iter(per_player.values())))):    # hand number = row count per player, like the builders
        if kind == "phase10":
            scores = [{"points": int(float(per_player[p.casefold()][k].get("Points") or 0)),
                       "made": per_player[p.casefold()][k]["Made phase?"].strip().upper() in TRUE} for p in players]
        else:
            won = [per_player[p.casefold()][k]["Won hand?"].strip().upper() in TRUE for p in players]
            left = [0 if w else int(float(per_player[p.casefold()][k].get("Cards left") or 0)) for p, w in zip(players, won)]
            scores = [{"points": 25 + 5 * sum(left) if w else 0, "won": w, "left": l} for w, l in zip(won, left)]
        hands.append({"no": k + 1, "scores": scores})
    game = {"game": kind, "label": label, "started_at": f"{date}T19:00:00", "finished": True,
            "players": players, "hands": hands}
    if kind == "skipbo":
        game.update(target=int(settings.get("target", 500)), stock=int(settings.get("stock", 30)))
    return game


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("game", choices=["phase10", "skipbo"])
    ap.add_argument("csv", type=Path)
    ap.add_argument("--label", required=True)
    ap.add_argument("--date", required=True, help="YYYY-MM-DD")
    args = ap.parse_args()
    url, key = os.environ.get("SCORES_API_URL"), os.environ.get("SCORES_FAMILY_KEY")
    if not url or not key:
        sys.exit("Set SCORES_API_URL and SCORES_FAMILY_KEY")

    game = build_game(args.game, args.csv, args.label, args.date)
    game_id = f"csv-{args.game}-{args.csv.stem}"
    req = urllib.request.Request(f"{url.rstrip('/')}/games/{game_id}", method="PUT",
                                 data=json.dumps(game).encode(),
                                 headers={"Content-Type": "application/json", "X-Family-Key": key})
    try:
        with urllib.request.urlopen(req, timeout=30):
            print(f'Imported "{args.label}" ({len(game["hands"])} hands) as {game_id}')
    except urllib.error.HTTPError as e:
        sys.exit(f"Import failed: {e.code} {e.read().decode()}")


if __name__ == "__main__":
    main()
