# Scorekeepers cloud

One shared SQLite database (Cloudflare D1) for the Phase 10, Skip-Bo and Five Crowns scorekeepers.
Every hand is saved to it automatically. There's nothing to export.

```
phone (any scorekeeper) ──save()──► localStorage ──outbox──► Worker (passcode check) ──► D1
                                                                        │
                                          nightly GitHub Action ◄── /export
                                          data/scorekeepers.json + .db in this repo
```

- **Offline is fine.** Each save goes to the phone first. Unsent saves wait in an outbox and go out when the signal returns. The ☁ pill in the corner shows the status.
- **Undo and edits sync too.** Each send replaces the whole game, so the cloud always matches the phone.
- **Backups:** D1 can roll back to any point in the last 7 days. The nightly Action also commits a readable JSON copy and a `.db` file here.

| File | What it is |
|---|---|
| `schema.sql` | Tables `players`, `games`, `hands` and the `game_results` view (place per game, by each game's own rule) |
| `src/index.js` | The Worker: `PUT /games/:id`, `GET /export`, `GET /health` |
| `cloud-sync.js` | Copied into each scorekeeper repo. Holds the outbox, the ☁ pill and the passcode |
| `backup.py` | Run nightly by `.github/workflows/scores-backup.yml` |
| `import_csv.py` | One-time import of old league CSVs |

## One-time setup (about 10 minutes)

You need a free [Cloudflare account](https://dash.cloudflare.com/sign-up) and Node.js on your computer.

```bash
cd maker-hub/scorekeepers-cloud
npm install
npx wrangler login                          # opens the browser to sign in to Cloudflare

npx wrangler d1 create scorekeepers         # prints a database_id
# paste that id into wrangler.toml, replacing REPLACE_WITH_ID_FROM_wrangler_d1_create

npx wrangler d1 execute scorekeepers --remote --file schema.sql
npx wrangler secret put FAMILY_KEY          # type the family passcode you want
npx wrangler deploy                         # prints https://scorekeepers.<you>.workers.dev
```

Check that it worked: open `https://scorekeepers.<you>.workers.dev/health`. It should say `ok`.

Then:

1. **Turn sync on in the apps:** set `var API_URL = "https://scorekeepers.<you>.workers.dev";` in `cloud-sync.js` in all three scorekeeper repos, or send Claude the URL. Until then, the apps behave exactly as before.
2. **Turn on the nightly backup:** in the maker-hub repo, go to Settings → Secrets and variables → Actions and add:
   - a **variable** `SCORES_API_URL` set to the Worker URL
   - a **secret** `SCORES_FAMILY_KEY` set to the passcode
3. **Bring in Phase 10 Game 1:**
   ```bash
   SCORES_API_URL=https://scorekeepers.<you>.workers.dev SCORES_FAMILY_KEY=yourpasscode \
     python import_csv.py phase10 ../../phase10-league/builder/game-1.csv --label "Game 1" --date 2026-11-20
   ```
4. **On each phone:** open any scorekeeper and tap **☁ Tap to connect**, or text everyone a link like
   `https://ovalt1nejenk1ns.github.io/phase10-league/#passcode=yourpasscode`. Once per phone covers all three apps.
   Five Crowns also sends that phone's past games the first time it connects.

## Day to day

Nothing to do. To query the data:

```bash
npx wrangler d1 execute scorekeepers --remote --command "SELECT * FROM game_results WHERE finished = 1"
```

Or open `data/scorekeepers.db` (updated nightly) in DB Browser for SQLite, pandas or the VS Code SQLite extension.

## Testing locally

```bash
echo 'FAMILY_KEY=test-pass' > .dev.vars
npx wrangler d1 execute scorekeepers --local --file schema.sql
npx wrangler dev --local                    # http://localhost:8787
```

The passcode is a light lock: the worst a leaked one allows is fake scores, and the Worker checks every save.
To change it, run `npx wrangler secret put FAMILY_KEY` again, update the GitHub secret, and reconnect each phone.
