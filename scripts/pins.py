"""Pin board: open GitHub issues labelled `pin` -> data/pins.json.

The issues are the source of truth (close one to unpin it). data/pins.json is a
snapshot that lives apart from feed.json, so the weekly refresh never touches it,
and it keeps each page's preview image/description even if the page later vanishes.

Issue body format (the 📌 buttons on the site pre-fill this):

    url: https://example.com/article
    topic: robotics
    kind: Article

    Anything else you type is kept as your note.

Run: python scripts/pins.py   (set GITHUB_TOKEN for higher rate limits)
"""
import json, os, re, sys, urllib.request
from html import unescape
from pathlib import Path
from urllib.parse import urljoin, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config

OUT = Path(__file__).resolve().parent.parent / "data" / "pins.json"
UA = "Mozilla/5.0 (maker-hub pin board)"
FIELD = re.compile(r"^\s*(url|topic|kind)\s*:\s*(.*?)\s*$", re.I)


def get(url, token=None, limit=None):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/vnd.github+json"
                                               if "api.github.com" in url else "text/html"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read(limit) if limit else r.read()


def fetch_issues():
    token = os.environ.get("GITHUB_TOKEN")
    issues, page = [], 1
    while True:
        url = (f"https://api.github.com/repos/{config.GITHUB_REPO}/issues"
               f"?labels={config.PIN_LABEL}&state=open&per_page=100&page={page}")
        batch = json.loads(get(url, token))
        issues += [i for i in batch if "pull_request" not in i]
        if len(batch) < 100:
            return issues
        page += 1


def parse_body(body):
    """Split the issue body into the url/topic/kind fields and a free-text note."""
    fields, note = {}, []
    body = re.sub(r"<!--.*?-->", "", body or "", flags=re.S)       # drop the template's hints
    for line in body.splitlines():
        m = FIELD.match(line)
        if m and m.group(1).lower() not in fields:
            fields[m.group(1).lower()] = m.group(2)
        else:
            note.append(line)
    if not fields.get("url"):                                       # pasted a bare link instead?
        m = re.search(r"https?://\S+", body)
        if m:
            fields["url"] = m.group(0).rstrip(").,>")
    return fields, "\n".join(note).strip()


def _meta(html, *names):
    for n in names:
        # <meta property="og:image" content="..."> in either attribute order
        for pat in (rf'<meta[^>]+(?:property|name)=["\']{n}["\'][^>]*content=["\']([^"\']+)',
                    rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]*(?:property|name)=["\']{n}["\']'):
            m = re.search(pat, html, re.I)
            if m:
                return unescape(m.group(1)).strip()
    return ""


def preview(url):
    """Best-effort image + description for a link. Never raises."""
    host = urlparse(url).netloc.lower()
    parts = urlparse(url).path.strip("/").split("/")
    image = ""
    if host == "github.com" and len(parts) >= 2:                    # GitHub's own repo cards look great
        image = f"https://opengraph.githubassets.com/1/{parts[0]}/{parts[1]}"
    try:
        html = get(url, limit=400_000).decode("utf-8", "replace")
    except Exception as e:
        print(f"  preview failed for {url}: {e}", file=sys.stderr)
        return {"image": image, "desc": ""}
    img = image or _meta(html, "og:image", "twitter:image", "twitter:image:src")
    return {"image": urljoin(url, img) if img else "",
            "desc": _meta(html, "og:description", "twitter:description", "description")[:280]}


def main():
    old = {p["url"]: p for p in json.loads(OUT.read_text(encoding="utf-8"))} if OUT.exists() else {}
    try:
        issues = fetch_issues()
    except Exception as e:
        # Keep the last good board rather than wiping it because GitHub hiccuped.
        print(f"Could not read pin issues ({e}); keeping existing {OUT.name}", file=sys.stderr)
        return
    pins = []
    for i in issues:
        f, note = parse_body(i["body"])
        url = f.get("url", "").strip("<> ")
        if not url.startswith("http"):
            print(f"  #{i['number']} has no url: line, skipped", file=sys.stderr)
            continue
        topic = f.get("topic", "").strip().lower()
        cached = old.get(url) or {}
        if not (cached.get("image") or cached.get("desc")):      # new link, or last attempt failed: (re)try
            cached = preview(url)
        pins.append({
            "id": i["number"], "title": i["title"].strip(), "url": url,
            "topic": topic if topic in config.TOPICS else "",
            "kind": (f.get("kind") or "Link").strip().title(),
            "note": note, "created": i["created_at"][:10], "issue": i["html_url"],
            "image": cached.get("image", ""), "desc": cached.get("desc", ""),
        })
    pins.sort(key=lambda p: p["id"], reverse=True)                  # newest pin first
    OUT.write_text(json.dumps(pins, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(pins)} pins -> {OUT}")


if __name__ == "__main__":
    main()
