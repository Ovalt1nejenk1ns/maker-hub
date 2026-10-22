"""One-time migration: move the Trends tab content out of index.html into trends.js.

Run from your local clone of maker-hub:
    python migrate_index.py            # edits index.html, saves index.html.bak first
    python migrate_index.py --dry-run  # just report what would change
"""
import re
import shutil
import sys
from pathlib import Path

INDEX = Path("index.html")
dry_run = "--dry-run" in sys.argv

html = INDEX.read_text(encoding="utf-8")  # be explicit: the emoji break Windows' default cp1252
original_len = len(html)

if "trends-render.js" in html:
    sys.exit("Already migrated (trends-render.js is referenced). Nothing to do.")

# 1) Empty the Trends section. Non-greedy .*? stops at the FIRST </section> after the
#    opening tag, which is correct because the Trends tab has no nested <section>s.
#    re.S lets . match newlines so the pattern can span the ~300 lines of cards.
trends_re = re.compile(r'(<section[^>]*id="tab-trends"[^>]*>)(.*?)(</section>)', re.S)
m = trends_re.search(html)
if not m:
    sys.exit('Could not find <section id="tab-trends">. Aborting, nothing written.')
removed = m.group(2)
html = trends_re.sub(r"\1\n  <!-- Rendered from trends.js by trends-render.js -->\n\3", html, count=1)

# 2) Add the "Trends refreshed ..." line at the top of What's New
whats_new_re = re.compile(r'(<section[^>]*id="tab-whats-new"[^>]*>)')
if not whats_new_re.search(html):
    sys.exit('Could not find <section id="tab-whats-new">. Aborting, nothing written.')
html = whats_new_re.sub(
    r'\1\n  <p id="trends-updated" class="changelog-date" style="margin:0 0 14px;"></p>',
    html, count=1)

# 3) Load trends.js + renderer right after data.js and BEFORE the main inline script,
#    so SEARCH_DATA exists when the renderer pushes trend items into it.
data_js_re = re.compile(r'(<script\s+src=["\']data\.js["\']\s*>\s*</script>)')
if not data_js_re.search(html):
    sys.exit('Could not find <script src="data.js"></script>. Aborting, nothing written.')
html = data_js_re.sub(
    r'\1\n<script src="trends.js"></script>\n<script src="trends-render.js"></script>',
    html, count=1)

# Sanity checks before writing anything
assert html.rstrip().endswith("</html>"), "File no longer ends with </html>"
assert html.count("<section") == html.count("</section>"), "Unbalanced <section> tags"

print(f"Removed {removed.count('trend-card')} trend cards ({len(removed):,} chars) from the Trends tab")
print(f"index.html: {original_len:,} -> {len(html):,} chars")

if dry_run:
    print("Dry run: nothing written.")
else:
    shutil.copy(INDEX, INDEX.with_suffix(".html.bak"))
    INDEX.write_text(html, encoding="utf-8")
    print("Wrote index.html (backup: index.html.bak)")
