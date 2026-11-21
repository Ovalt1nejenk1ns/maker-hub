/* Maker Hub: search, rotating tips and "surprise me". No dependencies. */
(function () {
  var root = document.body.getAttribute("data-root") || "";
  function pick(xs) { return xs[Math.floor(Math.random() * xs.length)]; }
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text) e.textContent = text;
    return e;
  }
  function href(u) { return /^https?:/.test(u) ? u : root + u; }

  /* Did you know? */
  var tip = document.getElementById("tip");
  if (tip) {
    var tips = JSON.parse(tip.getAttribute("data-tips") || "[]"), last = null;
    var show = function () {
      if (!tips.length) return;
      var t = pick(tips);
      if (tips.length > 1) while (t === last) t = pick(tips);
      last = t;
      tip.querySelector(".tip-text").textContent = t.t;
      tip.querySelector(".tip-src").textContent = t.s;
    };
    show();
    var next = tip.querySelector("button");
    if (next) { next.hidden = false; next.addEventListener("click", show); }
  }

  /* Search */
  var box = document.getElementById("q"), out = document.getElementById("results"), index = null;
  if (box && out) {
    var load = function () {
      if (index) return Promise.resolve(index);
      return fetch(root + "search.json").then(function (r) { return r.json(); })
        .then(function (d) {
          d.forEach(function (x) { x.h = (x.t + " " + x.k + " " + x.s).toLowerCase(); });
          index = d; return d;
        });
    };
    var run = function () {
      var words = box.value.toLowerCase().split(/\s+/).filter(Boolean);
      out.textContent = "";
      if (!words.length) { out.hidden = true; return; }
      load().then(function (d) {
        var hits = d.filter(function (x) { return words.every(function (w) { return x.h.indexOf(w) >= 0; }); });
        out.textContent = "";
        if (!hits.length) out.appendChild(el("p", "muted", "Nothing found. Try a shorter word."));
        hits.slice(0, 12).forEach(function (x) {
          var a = el("a", "hit");
          a.href = href(x.u);
          a.appendChild(el("span", "kind", x.k));
          a.appendChild(el("span", "", x.t.length > 110 ? x.t.slice(0, 107) + "…" : x.t));
          a.appendChild(el("span", "muted", x.s));
          out.appendChild(a);
        });
        if (hits.length > 12) out.appendChild(el("p", "muted", (hits.length - 12) + " more. Add a word to narrow it down."));
        out.hidden = false;
      }).catch(function () {
        out.textContent = ""; out.appendChild(el("p", "muted", "Search could not load.")); out.hidden = false;
      });
    };
    box.addEventListener("input", run);
    box.addEventListener("focus", function () { load().catch(function () {}); if (box.value) run(); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { out.hidden = true; box.blur(); }
      var typing = /INPUT|TEXTAREA/.test(document.activeElement.tagName);
      if ((e.key === "/" && !typing) || (e.key === "k" && (e.metaKey || e.ctrlKey))) { e.preventDefault(); box.focus(); box.select(); }
    });
    document.addEventListener("click", function (e) {
      if (!e.target.closest(".search")) out.hidden = true;
    });
  }

  /* Surprise me: highlight a random project idea on a topic page */
  var sb = document.getElementById("surprise");
  if (sb) {
    sb.hidden = false;
    sb.addEventListener("click", function () {
      var cards = [].slice.call(document.querySelectorAll(".idea"));
      if (!cards.length) return;
      var cur = document.querySelector(".idea.pick"), c = pick(cards);
      if (cards.length > 1) while (c === cur) c = pick(cards);
      if (cur) cur.classList.remove("pick");
      c.classList.add("pick");
      c.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  }

  /* "2026-11-20" -> "yesterday" / "3d ago", computed in the browser so it stays true between weekly builds */
  [].forEach.call(document.querySelectorAll("time[data-ago]"), function (t) {
    var d = new Date(t.getAttribute("datetime") + "T12:00:00");
    if (isNaN(d)) return;
    var days = Math.round((Date.now() - d) / 864e5);
    t.title = t.getAttribute("datetime");
    t.textContent = days <= 0 ? "today" : days === 1 ? "yesterday" : days < 14 ? days + "d ago"
      : days < 60 ? Math.round(days / 7) + "w ago" : t.getAttribute("datetime");
  });

  /* Sticky section nav: highlight the section currently on screen */
  var navLinks = [].slice.call(document.querySelectorAll(".subnav a[href^='#']"));
  if (navLinks.length && "IntersectionObserver" in window) {
    var byId = {};
    navLinks.forEach(function (a) { byId[a.getAttribute("href").slice(1)] = a; });
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        navLinks.forEach(function (a) { a.classList.remove("on"); });
        var a = byId[en.target.id];
        if (a) { a.classList.add("on"); a.scrollIntoView({ block: "nearest", inline: "nearest" }); }
      });
    }, { rootMargin: "-25% 0px -65% 0px" });   // a section counts as "current" when it crosses the upper third
    Object.keys(byId).forEach(function (id) { var s = document.getElementById(id); if (s) spy.observe(s); });
  }

  /* ---------- Pin board: one-click pinning through the GitHub API ----------
     A pin is a GitHub issue labelled "pin". With a token saved in this browser we create it
     directly; the Action then snapshots it into data/pins.json on its next run. */
  var REPO = document.body.getAttribute("data-repo"), LABEL = document.body.getAttribute("data-label") || "pin";
  var API = "https://api.github.com/repos/" + REPO;
  function store(k, v) {            // localStorage can throw (private mode, blocked storage)
    try {
      if (v === undefined) return localStorage.getItem(k);
      if (v === null) localStorage.removeItem(k); else localStorage.setItem(k, v);
    } catch (e) { return null; }
  }
  function token() { return store("mh_pin_token"); }
  function pinnedMap() { try { return JSON.parse(store("mh_pinned") || "{}"); } catch (e) { return {}; } }
  function savePinned(m) { store("mh_pinned", JSON.stringify(m)); }
  var built = [];
  try { built = JSON.parse(document.getElementById("pinned-urls").textContent); } catch (e) {}
  function isPinned(u) { return built.indexOf(u) >= 0 || !!pinnedMap()[u]; }
  var boardHref = root + "board/index.html";

  var toastEl = document.getElementById("toast"), toastTimer;
  function toast(text, linkText) {
    if (!toastEl) return;
    toastEl.textContent = text;
    if (linkText) { var a = el("a", "", linkText); a.href = boardHref; toastEl.appendChild(a); }
    toastEl.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.hidden = true; }, 4500);
  }

  function gh(method, path, body, tok) {
    var h = { Accept: "application/vnd.github+json" };
    if (tok) h.Authorization = "Bearer " + tok;
    if (body) h["Content-Type"] = "application/json";
    return fetch(API + path, { method: method, headers: h, body: body ? JSON.stringify(body) : undefined })
      .then(function (r) {
        return r.json().catch(function () { return {}; }).then(function (d) {
          if (!r.ok) { var e = new Error(d.message || "HTTP " + r.status); e.status = r.status; throw e; }
          return d;
        });
      });
  }

  function markButtons() {
    [].forEach.call(document.querySelectorAll(".pinbtn[data-url]"), function (b) {
      var on = isPinned(b.getAttribute("data-url"));
      b.classList.toggle("pinned", on);
      b.title = on ? "On your board" : "Pin to my board";
    });
  }
  markButtons();

  /* One-time setup dialog */
  var dlg = document.getElementById("connect"), pending = null, pendingBtn = null;
  function openConnect(p, btn, msg) {
    if (!dlg || !dlg.showModal) { if (p && p.fallback) window.open(p.fallback, "_blank"); return; }
    pending = p; pendingBtn = btn;
    dlg.querySelector(".fallback").href = (p && p.fallback) || ("https://github.com/" + REPO + "/issues/new?labels=" + LABEL);
    dlg.querySelector(".fallback").hidden = !p;
    dlg.querySelector(".connect-msg").textContent = msg || "";
    dlg.showModal();
    dlg.querySelector("#tok").focus();
  }
  if (dlg) {
    dlg.querySelector("[data-act=save]").addEventListener("click", function () {
      var tok = dlg.querySelector("#tok").value.trim(), msg = dlg.querySelector(".connect-msg");
      if (!tok) { msg.textContent = "Paste the token first."; return; }
      msg.textContent = "Checking…";
      gh("GET", "", null, tok).then(function () {
        store("mh_pin_token", tok);
        dlg.querySelector("#tok").value = "";
        dlg.close();
        showConn();
        if (pending) doPin(pending, pendingBtn); else toast("Connected ✓ One-click pinning is on.");
      }).catch(function () { msg.textContent = "GitHub didn't accept that token. Copy it again and paste the whole thing."; });
    });
    dlg.querySelector(".fallback").addEventListener("click", function () { dlg.close(); });
  }

  function doPin(p, btn) {
    if (isPinned(p.url)) { toast("Already on your board. ", "Open board →"); return Promise.resolve(); }
    if (!token()) { openConnect(p, btn); return Promise.resolve(); }
    if (btn) btn.classList.add("busy");
    var body = "url: " + p.url + "\ntopic: " + (p.topic || "") + "\nkind: " + (p.kind || "Link") + "\n\n" + (p.note || "");
    return gh("POST", "/issues", { title: p.title || p.url, body: body, labels: [LABEL] }, token())
      .then(function (d) {
        var m = pinnedMap(); m[p.url] = d.number; savePinned(m);
        markButtons();
        toast("📌 Pinned: " + (p.title || p.url).slice(0, 60) + "  ", "Open board →");
        if (board) addCard(fromIssue(d), true);
      })
      .catch(function (e) {
        if (e.status === 401) { store("mh_pin_token", null); openConnect(p, btn, "That token has expired or was revoked. Make a new one."); }
        else if (e.status === 403 || e.status === 404) openConnect(p, btn, "That token can't create issues on maker-hub. Make sure maker-hub is selected and Issues is set to Read and write.");
        else toast("Couldn't pin (" + e.message + "). Try again in a moment.");
      })
      .then(function () { if (btn) btn.classList.remove("busy"); });
  }

  document.addEventListener("click", function (e) {
    var b = e.target.closest(".pinbtn[data-url]");
    if (!b) return;
    e.preventDefault();
    doPin({ title: b.getAttribute("data-title"), url: b.getAttribute("data-url"), topic: b.getAttribute("data-topic"),
            kind: b.getAttribute("data-kind"), fallback: b.href }, b);
  });

  /* Board page */
  var board = document.getElementById("pins"), meta = {};
  try { meta = JSON.parse(document.getElementById("topic-meta").textContent); } catch (e) {}

  function fromIssue(i) {                       // same format scripts/pins.py reads
    var f = {}, note = [];
    (i.body || "").replace(/<!--[\s\S]*?-->/g, "").split("\n").forEach(function (line) {
      var m = line.match(/^\s*(url|topic|kind)\s*:\s*(.*?)\s*$/i);
      if (m && !(m[1].toLowerCase() in f)) f[m[1].toLowerCase()] = m[2]; else note.push(line);
    });
    if (!f.url) { var m = (i.body || "").match(/https?:\/\/\S+/); if (m) f.url = m[0]; }
    return { id: i.number, title: i.title, url: f.url || "", topic: meta[(f.topic || "").toLowerCase()] ? f.topic.toLowerCase() : "",
             kind: f.kind || "Link", note: note.join("\n").trim(), created: (i.created_at || "").slice(0, 10), issue: i.html_url };
  }

  function addCard(p, fresh) {
    if (!board || !p.url || board.querySelector('[data-issue="' + p.id + '"]')) return;
    var art = el("article", "pin" + (p.topic ? " t-" + p.topic : "")), body = el("div", "pin-body");
    art.setAttribute("data-t", p.topic); art.setAttribute("data-k", p.kind); art.setAttribute("data-issue", p.id);
    var tags = el("p", "pin-tags");
    tags.appendChild(el("span", "tag", p.kind));
    if (p.topic) { tags.appendChild(document.createTextNode(" ")); tags.appendChild(el("span", "tag topic", meta[p.topic].icon + " " + meta[p.topic].short)); }
    if (fresh) { tags.appendChild(document.createTextNode(" ")); tags.appendChild(el("span", "tag fresh", "just pinned")); }
    var h = el("h3"), a = el("a", "", p.title || p.url); a.href = p.url; h.appendChild(a);
    body.appendChild(tags); body.appendChild(h);
    if (p.note) body.appendChild(el("p", "pin-note", p.note));
    var foot = el("p", "meta mono pin-foot", "today · " + (p.url.split("/")[2] || "") + " ");
    var acts = el("span", "pin-acts"), ed = el("a", "", "edit"), un = el("a", "unpin", "unpin");
    ed.href = un.href = p.issue; ed.target = un.target = "_blank";
    acts.appendChild(ed); acts.appendChild(document.createTextNode(" ")); acts.appendChild(un); foot.appendChild(acts);
    body.appendChild(foot); art.appendChild(body);
    board.insertBefore(art, board.firstChild);
    refreshCounts();
  }

  function refreshCounts() {
    var n = board.querySelectorAll(".pin").length, all = document.querySelector('.filters [data-f="*"] b');
    if (all) all.textContent = n;
    var f = document.querySelector(".filters"); if (f) f.hidden = n === 0;
    var empty = document.querySelector(".empty-board"); if (empty) empty.hidden = n > 0;
  }

  var conn = document.querySelector(".conn");
  function showConn() {
    if (!conn) return;
    conn.textContent = "";
    var a = el("a", "", token() ? "disconnect" : "connect GitHub");
    a.href = "#";
    a.addEventListener("click", function (e) {
      e.preventDefault();
      if (token()) { store("mh_pin_token", null); showConn(); toast("Disconnected. Pins stay on your board."); }
      else openConnect(null, null);
    });
    conn.appendChild(document.createTextNode(token() ? "● One-click pinning on · " : "○ One-click pinning off · "));
    conn.appendChild(a);
  }

  if (board) {
    showConn();
    // Live sync: show pins made since the last build and drop ones closed on GitHub.
    gh("GET", "/issues?labels=" + LABEL + "&state=open&per_page=100", null, token()).then(function (issues) {
      var live = {}, m = {};
      issues.filter(function (i) { return !i.pull_request; }).map(fromIssue).forEach(function (p) { live[p.id] = 1; if (p.url) m[p.url] = p.id; });
      [].forEach.call(board.querySelectorAll(".pin"), function (c) { if (!live[c.getAttribute("data-issue")]) c.remove(); });
      issues.map(fromIssue).reverse().forEach(function (p) { addCard(p, true); });
      built = []; savePinned(m); refreshCounts();
    }).catch(function () {});

    board.addEventListener("click", function (e) {
      var un = e.target.closest(".unpin");
      if (!un || !token()) return;              // no token: the link opens the issue on GitHub to close it there
      e.preventDefault();
      var card = un.closest(".pin"), id = card.getAttribute("data-issue");
      gh("PATCH", "/issues/" + id, { state: "closed", state_reason: "completed" }, token()).then(function () {
        var m = pinnedMap(); Object.keys(m).forEach(function (u) { if (String(m[u]) === id) delete m[u]; }); savePinned(m);
        card.remove(); refreshCounts(); toast("Unpinned.");
      }).catch(function (err) { toast("Couldn't unpin (" + err.message + ")."); });
    });

    var form = document.getElementById("add-form");
    document.getElementById("add-link").addEventListener("click", function () {
      form.hidden = !form.hidden; if (!form.hidden) form.url.focus();
    });
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      doPin({ url: form.url.value.trim(), title: form.title.value.trim(), topic: form.topic.value,
              kind: form.kind.value, note: form.note.value.trim() }).then(function () { form.reset(); form.hidden = true; });
    });

    // Bookmarklet lands here as board/?url=…&title=…: pin it straight away.
    var qs = new URLSearchParams(location.search);
    if (qs.get("url")) {
      history.replaceState(null, "", location.pathname);
      doPin({ url: qs.get("url"), title: qs.get("title") || "", kind: "Article" });
    }
  }

  /* Board filters (query cards each time, so live-added pins are included) */
  var filters = document.querySelector(".filters");
  if (filters) {
    filters.addEventListener("click", function (e) {
      var b = e.target.closest("button"); if (!b) return;
      [].forEach.call(filters.querySelectorAll("button"), function (x) { x.classList.toggle("on", x === b); });
      var f = b.getAttribute("data-f"), shown = 0;
      [].forEach.call(document.querySelectorAll(".pin"), function (p) {
        var ok = f === "*" || (f.slice(0, 2) === "t:" ? p.getAttribute("data-t") === f.slice(2) : p.getAttribute("data-k") === f.slice(2));
        p.hidden = !ok; if (ok) shown++;
      });
      var empty = document.querySelector(".empty-filter"); if (empty) empty.hidden = shown > 0;
    });
  }
  [].forEach.call(document.querySelectorAll(".pin-img img"), function (img) {
    var drop = function () { img.parentNode.remove(); };
    if (img.complete && !img.naturalWidth) drop(); else img.addEventListener("error", drop);
  });

  /* Home page: random pickers (rabbit holes, project ideas) */
  [].forEach.call(document.querySelectorAll(".roller"), function (box) {
    var items = JSON.parse(box.getAttribute("data-items") || "[]"), shown = null;
    var roll = function () {
      if (!items.length) return;
      var i = pick(items);
      if (items.length > 1) while (i === shown) i = pick(items);
      shown = i;
      var a = box.querySelector(".idea-title");
      a.textContent = i.t; a.href = href(i.u);
      box.querySelector(".idea-desc").textContent = i.d;
      box.querySelector(".idea-meta").textContent = i.m ? i.s + " · " + i.m : i.s;
    };
    roll();
    var again = box.querySelector("button");
    if (again) { again.hidden = false; again.addEventListener("click", roll); }
  });
})();
