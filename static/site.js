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

  /* Board: filter pins by topic or kind; hide preview images that fail to load */
  var filters = document.querySelector(".filters");
  if (filters) {
    var pins = [].slice.call(document.querySelectorAll(".pin")), empty = document.querySelector(".empty-filter");
    filters.addEventListener("click", function (e) {
      var b = e.target.closest("button"); if (!b) return;
      [].forEach.call(filters.querySelectorAll("button"), function (x) { x.classList.toggle("on", x === b); });
      var f = b.getAttribute("data-f"), shown = 0;
      pins.forEach(function (p) {
        var ok = f === "*" || (f.slice(0, 2) === "t:" ? p.getAttribute("data-t") === f.slice(2) : p.getAttribute("data-k") === f.slice(2));
        p.hidden = !ok; if (ok) shown++;
      });
      if (empty) empty.hidden = shown > 0;
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
