-- One shared database for every scorekeeper (Cloudflare D1 = SQLite).
-- Apply with: npx wrangler d1 execute scorekeepers --remote --file schema.sql

CREATE TABLE IF NOT EXISTS players (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE          -- "liz" and "Liz" are the same person
);

CREATE TABLE IF NOT EXISTS games (
    id         TEXT PRIMARY KEY,                      -- made by the app when the game starts
    game       TEXT NOT NULL CHECK (game IN ('phase10', 'skipbo', 'fivecrowns')),
    label      TEXT NOT NULL DEFAULT '',
    started_at TEXT NOT NULL,                         -- ISO timestamp from the phone
    finished   INTEGER NOT NULL DEFAULT 0 CHECK (finished IN (0, 1)),
    target     INTEGER,                               -- Skip-Bo only: points to win
    stock      INTEGER,                               -- Skip-Bo only: stock pile size
    updated_at TEXT NOT NULL
);

-- One row per player per hand. Five Crowns numbers its rounds 3-13 like the app.
-- Columns that don't apply to a game are NULL (made_phase is Phase 10 only, and so on).
CREATE TABLE IF NOT EXISTS hands (
    game_id    TEXT NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    hand_no    INTEGER NOT NULL,
    player_id  INTEGER NOT NULL REFERENCES players(id),
    seat       INTEGER NOT NULL,                      -- keeps the table order from the app
    points     INTEGER NOT NULL CHECK (points >= 0),
    made_phase INTEGER CHECK (made_phase IN (0, 1)),
    won_hand   INTEGER CHECK (won_hand IN (0, 1)),
    cards_left INTEGER CHECK (cards_left >= 0),
    PRIMARY KEY (game_id, hand_no, player_id)
);

-- Each player's result in each game, ranked by that game's own rule:
--   Phase 10: most phases, then fewest points.  Skip-Bo: most points.  Five Crowns: fewest points.
CREATE VIEW IF NOT EXISTS game_results AS
SELECT g.id AS game_id, g.game, g.label, g.started_at, g.finished, p.name AS player,
       SUM(h.points) AS points, SUM(h.made_phase) AS phases, SUM(h.won_hand) AS hands_won,
       COUNT(*) AS hands,
       RANK() OVER (
           PARTITION BY g.id
           ORDER BY CASE g.game WHEN 'phase10' THEN -SUM(h.made_phase) ELSE 0 END,
                    CASE g.game WHEN 'skipbo'  THEN -SUM(h.points) ELSE SUM(h.points) END
       ) AS place
FROM hands h
JOIN games g   ON g.id = h.game_id
JOIN players p ON p.id = h.player_id
GROUP BY g.id, p.id;
