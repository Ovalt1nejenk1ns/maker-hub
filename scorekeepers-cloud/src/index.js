// Scorekeepers API: the three scorekeeper apps save games here, into one D1 (SQLite) database.
//
//   PUT /games/:id   save the whole current state of one game (replaces what was there)
//   GET /export      every table as JSON, for the nightly backup
//   GET /health      "ok", to check the deploy
//
// Writes and the export need the family passcode in the X-Family-Key header.
// Settings: FAMILY_KEY (a secret) and ALLOWED_ORIGINS (in wrangler.toml).

const GAMES = new Set(["phase10", "skipbo", "fivecrowns"]);
const MAX_BODY = 64 * 1024;          // a long game is ~10 KB; anything far bigger is junk
const ID = /^[A-Za-z0-9_.:-]{8,64}$/;

export default {
  async fetch(request, env) {
    const cors = corsHeaders(request, env);
    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });

    const reply = (body, status = 200) =>
      new Response(typeof body === "string" ? body : JSON.stringify(body), {
        status,
        headers: { ...cors, "Content-Type": typeof body === "string" ? "text/plain" : "application/json" },
      });

    const url = new URL(request.url);
    try {
      if (url.pathname === "/health") return reply("ok");

      if (!env.FAMILY_KEY || request.headers.get("X-Family-Key") !== env.FAMILY_KEY) {
        return reply({ error: "Wrong or missing family passcode" }, 401);
      }

      const m = url.pathname.match(/^\/games\/([^/]+)$/);
      if (m && request.method === "PUT") {
        const text = await request.text();
        if (text.length > MAX_BODY) return reply({ error: "Game is too large" }, 413);
        let body;
        try { body = JSON.parse(text); } catch { return reply({ error: "Body is not JSON" }, 400); }
        const problem = validate(decodeURIComponent(m[1]), body);
        if (problem) return reply({ error: problem }, 400);
        const id = decodeURIComponent(m[1]);
        const existing = await env.DB.prepare("SELECT game FROM games WHERE id = ?").bind(id).first();
        if (existing && existing.game !== body.game) {
          return reply({ error: `That id belongs to a ${existing.game} game` }, 409);   // never mix games
        }
        await saveGame(env.DB, id, body);
        return reply({ saved: true });
      }

      if (url.pathname === "/export" && request.method === "GET") {
        const [players, games, hands] = await env.DB.batch([
          env.DB.prepare("SELECT * FROM players ORDER BY id"),
          env.DB.prepare("SELECT * FROM games ORDER BY started_at"),
          env.DB.prepare("SELECT * FROM hands ORDER BY game_id, hand_no, seat"),
        ]);
        return reply({ exported_at: new Date().toISOString(), players: players.results,
                       games: games.results, hands: hands.results });
      }

      return reply({ error: "Not found" }, 404);
    } catch (err) {
      console.error(err);
      return reply({ error: "Server error" }, 500);
    }
  },
};

function corsHeaders(request, env) {
  // Only our own pages may call the API from a browser.
  const allowed = (env.ALLOWED_ORIGINS || "").split(",").map((s) => s.trim());
  const origin = request.headers.get("Origin");
  return {
    "Access-Control-Allow-Origin": allowed.includes(origin) ? origin : allowed[0] || "",
    "Access-Control-Allow-Methods": "GET, PUT, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, X-Family-Key",
    "Access-Control-Max-Age": "86400",
    Vary: "Origin",
  };
}

const isInt = (v, lo, hi) => Number.isInteger(v) && v >= lo && v <= hi;

// Check everything before touching the database, so a buggy app or a stranger can't store junk.
function validate(id, g) {
  if (!ID.test(id)) return "Bad game id";
  if (!g || !GAMES.has(g.game)) return "Unknown game type";
  if (typeof g.started_at !== "string" || isNaN(Date.parse(g.started_at))) return "Bad started_at";
  if (!Array.isArray(g.players) || g.players.length < 2 || g.players.length > 10) return "Need 2-10 players";
  if (g.players.some((p) => typeof p !== "string" || !p.trim() || p.length > 40)) return "Bad player name";
  if (new Set(g.players.map((p) => p.trim().toLowerCase())).size !== g.players.length) return "Duplicate player names";
  if (!Array.isArray(g.hands) || g.hands.length > 100) return "Bad hands list";
  for (const h of g.hands) {
    if (!h || !isInt(h.no, 1, 100) || !Array.isArray(h.scores) || h.scores.length !== g.players.length) {
      return "Each hand needs a number and one score per player";
    }
    for (const s of h.scores) {
      if (!s || !isInt(s.points, 0, 5000)) return "Points must be whole numbers from 0 to 5000";
      if (s.left !== undefined && !isInt(s.left, 0, 100)) return "Bad cards-left value";
    }
  }
  return "";
}

async function saveGame(db, id, g) {
  const players = g.players.map((p) => p.trim());
  // Flatten to one JSON array so a single SQL statement can insert every row via json_each().
  const rows = g.hands.flatMap((h) => h.scores.map((s, seat) => ({
    no: h.no, seat, name: players[seat], points: s.points,
    made: s.made === undefined ? null : s.made ? 1 : 0,
    won: s.won === undefined ? null : s.won ? 1 : 0,
    left: s.left === undefined ? null : s.left,
  })));
  const now = new Date().toISOString();

  // batch() runs as one transaction: the game is saved completely or not at all.
  await db.batch([
    db.prepare("INSERT OR IGNORE INTO players (name) SELECT value FROM json_each(?)")
      .bind(JSON.stringify(players)),
    db.prepare(`INSERT INTO games (id, game, label, started_at, finished, target, stock, updated_at)
                VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8)
                ON CONFLICT (id) DO UPDATE SET
                  label = excluded.label, finished = excluded.finished, target = excluded.target,
                  stock = excluded.stock, updated_at = excluded.updated_at
                WHERE games.game = excluded.game`)            // a game can't change type
      .bind(id, g.game, String(g.label || "").slice(0, 80), g.started_at, g.finished ? 1 : 0,
            g.target ?? null, g.stock ?? null, now),
    // Belt and braces: even in a race, only clear hands of a game of this same type.
    db.prepare("DELETE FROM hands WHERE game_id = ?1 AND (SELECT game FROM games WHERE id = ?1) = ?2")
      .bind(id, g.game),
    db.prepare(`INSERT INTO hands (game_id, hand_no, player_id, seat, points, made_phase, won_hand, cards_left)
                SELECT ?1, json_extract(r.value, '$.no'), p.id, json_extract(r.value, '$.seat'),
                       json_extract(r.value, '$.points'), json_extract(r.value, '$.made'),
                       json_extract(r.value, '$.won'), json_extract(r.value, '$.left')
                FROM json_each(?2) AS r
                JOIN players p ON p.name = json_extract(r.value, '$.name')
                WHERE (SELECT game FROM games WHERE id = ?1) = ?3`)
      .bind(id, JSON.stringify(rows), g.game),
  ]);
}
