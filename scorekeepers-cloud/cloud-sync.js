/* Cloud sync for the scorekeepers. The same file is copied into each scorekeeper repo.

   The app still saves to localStorage first, so it works with no signal. Every save also
   goes into an "outbox" here, and the outbox is sent to the family scores database
   (scorekeepers-cloud in the maker-hub repo) whenever the phone is online. Only the latest
   copy of each game is kept in the outbox, because each send replaces the whole game.

   All three apps are served from ovalt1nejenk1ns.github.io, so they share localStorage:
   the passcode is entered once per phone and covers every app. */
(function () {
  "use strict";

  // Set this to your Worker's address after deploying (see scorekeepers-cloud/README.md).
  // While it's empty, sync is switched off and the apps behave exactly as before.
  var API_URL = "";

  var KEY = "scorekeepers:passcode", OUTBOX = "scorekeepers:outbox";
  var pill = null, busy = false, timer = null;

  function get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function set(k, v) { try { if (v === null) localStorage.removeItem(k); else localStorage.setItem(k, v); } catch (e) {} }
  function outbox() { try { return JSON.parse(get(OUTBOX) || "{}"); } catch (e) { return {}; } }
  function newId() {
    return (window.crypto && crypto.randomUUID) ? crypto.randomUUID()
      : Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 10);
  }

  // A text-message link like https://.../phase10-league/#passcode=abc stores the passcode on that phone.
  var m = location.hash.match(/passcode=([^&]+)/);
  if (m) {
    set(KEY, decodeURIComponent(m[1]));
    history.replaceState(null, "", location.pathname + location.search);
  }

  function status(text, title) {
    if (!API_URL) return;
    if (!pill) {
      pill = document.createElement("button");
      pill.type = "button";
      pill.style.cssText = "position:fixed;left:10px;bottom:10px;z-index:9999;font:12px/1.2 system-ui,sans-serif;" +
        "padding:6px 10px;border-radius:999px;border:1px solid rgba(0,0,0,.15);background:#fff;color:#222;" +
        "box-shadow:0 2px 8px rgba(0,0,0,.15);cursor:pointer;opacity:.9";
      pill.addEventListener("click", function () {
        if (!get(KEY)) askPasscode(); else flush();
      });
      document.body.appendChild(pill);
    }
    pill.textContent = text;
    pill.title = title || "";
  }

  function askPasscode() {
    var code = window.prompt("Family passcode for saving scores to the cloud (once per phone):");
    if (code && code.trim()) { set(KEY, code.trim()); flush(); }
  }

  function render() {
    var waiting = Object.keys(outbox()).length;
    if (!get(KEY)) status("☁ Tap to connect", "Enter the family passcode to save scores to the cloud");
    else if (waiting) status("☁ " + waiting + " waiting to sync", "Saved on this phone. Sends automatically when online.");
    else status("☁ Synced", "Every game on this phone is saved in the cloud");
  }

  // Send everything in the outbox, oldest first. Anything that fails stays for the next try.
  function flush() {
    if (!API_URL || busy || !get(KEY)) { render(); return; }
    var box = outbox(), ids = Object.keys(box);
    if (!ids.length) { render(); return; }
    busy = true;
    status("☁ Syncing…");
    var chain = Promise.resolve();
    ids.forEach(function (id) {
      chain = chain.then(function () {
        return fetch(API_URL + "/games/" + encodeURIComponent(id), {
          method: "PUT",
          headers: { "Content-Type": "application/json", "X-Family-Key": get(KEY) },
          body: JSON.stringify(box[id]),
        }).then(function (r) {
          if (r.status === 401) { set(KEY, null); throw new Error("passcode"); }
          if (r.ok || r.status === 400 || r.status === 409) {
            // Sent, or rejected for good (bad data won't get better by retrying): drop it,
            // unless the app saved a newer copy of this game while we were sending.
            var now = outbox();
            if (now[id] && now[id]._saved === box[id]._saved) { delete now[id]; set(OUTBOX, JSON.stringify(now)); }
            if (!r.ok) console.warn("Cloud sync rejected game", id, r.status);
          }
        });
      });
    });
    chain.catch(function (e) {
      if (e && e.message === "passcode") window.setTimeout(askPasscode, 0);
    }).then(function () {
      busy = false;
      render();
      if (Object.keys(outbox()).length && !timer) {          // still waiting: try again in 30 s
        timer = window.setTimeout(function () { timer = null; flush(); }, 30000);
      }
    });
  }

  window.CloudSync = {
    enabled: !!API_URL,                 // false until API_URL is set, so apps can skip one-time work
    newId: newId,
    // game: { id, game, label, started_at, finished, players: [...], hands: [{ no, scores: [...] }] }
    save: function (game) {
      if (!API_URL || !game || !game.id) return;
      var box = outbox();
      game._saved = Date.now();
      box[game.id] = game;
      set(OUTBOX, JSON.stringify(box));
      flush();
    },
    flush: flush,
  };

  window.addEventListener("online", flush);
  document.addEventListener("visibilitychange", function () { if (!document.hidden) flush(); });
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", flush);
  else flush();
})();
