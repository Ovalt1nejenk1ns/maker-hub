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
      if (e.key === "/" && !/INPUT|TEXTAREA/.test(document.activeElement.tagName)) { e.preventDefault(); box.focus(); }
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

  /* Home page: random project idea from any topic */
  var hi = document.getElementById("home-idea");
  if (hi) {
    var ideas = JSON.parse(hi.getAttribute("data-ideas") || "[]"), shown = null;
    var roll = function () {
      if (!ideas.length) return;
      var i = pick(ideas);
      if (ideas.length > 1) while (i === shown) i = pick(ideas);
      shown = i;
      var a = hi.querySelector(".idea-title");
      a.textContent = i.t; a.href = href(i.u);
      hi.querySelector(".idea-desc").textContent = i.d;
      hi.querySelector(".idea-meta").textContent = i.s + " · " + i.m;
    };
    roll();
    var again = hi.querySelector("button");
    if (again) { again.hidden = false; again.addEventListener("click", roll); }
  }
})();
