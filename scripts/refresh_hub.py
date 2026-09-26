"""
refresh_hub.py
Reads index.html and trends_data.json, calls the Claude API to rewrite
the Trends and What's New sections with fresh content, then saves the
updated index.html back to disk.
"""

import os
import re
import json
import sys
import anthropic
from datetime import datetime


# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_section(html: str, section_id: str):
    """Return (section_html, start_index, end_index) for a tab-panel by ID."""
    pattern = rf'(<section[^>]*\bid="{section_id}"[^>]*>)(.*?)(</section>)'
    m = re.search(pattern, html, re.DOTALL)
    if not m:
        return None, -1, -1
    return m.group(0), m.start(), m.end()


def replace_section(html: str, section_id: str, new_content: str) -> str:
    """Swap out one tab-panel section by ID."""
    pattern = rf'<section[^>]*\bid="{section_id}"[^>]*>.*?</section>'
    result, count = re.subn(pattern, new_content, html, flags=re.DOTALL)
    if count == 0:
        raise ValueError(f"Section id='{section_id}' not found in HTML")
    return result


def build_prompt(today: str, trends_data: dict, trends_html: str, whats_new_html: str) -> str:
    return f"""You are updating two sections of a single-file HTML maker resources hub site.

Today's date: {today}

## Fresh trend data (use this to populate the Trends section)

```json
{json.dumps(trends_data, indent=2)}
```

---

## Current TRENDS section (id="tab-trends") — replace this with fresh content

{trends_html}

---

## Current WHAT'S NEW section (id="tab-whats-new") — update date only

{whats_new_html}

---

## Instructions

1. **Trends section**: Rewrite it using the fresh data above. Keep the EXACT same HTML structure and CSS classes that are already in the section (`.trend-card`, `.res-card`, `.section-head`, etc.). Update any "Trending —" header to say "Trending — {today}". Represent GitHub repos, Reddit top posts, and HN highlights in their respective cards.

2. **What's New section**: Update ONLY the changelog date / "last updated" text to today ({today}). Do not change any other content in this section.

3. Return ONLY the two updated sections with NO other text, NO markdown code fences, NO explanation. Separate them with exactly this delimiter on its own line:
---SECTION-BREAK---

Output format:
<complete updated tab-trends section from opening <section> tag to closing </section>>
---SECTION-BREAK---
<complete updated tab-whats-new section from opening <section> tag to closing </section>>"""


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set.")
        sys.exit(1)

    # Load files
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    with open("trends_data.json", "r", encoding="utf-8") as f:
        trends_data = json.load(f)

    today = datetime.now().strftime("%B %d, %Y")

    # Extract sections
    trends_html, _, _ = extract_section(html, "tab-trends")
    whats_new_html, _, _ = extract_section(html, "tab-whats-new")

    if not trends_html:
        print("ERROR: Could not find id='tab-trends' in index.html")
        sys.exit(1)
    if not whats_new_html:
        print("ERROR: Could not find id='tab-whats-new' in index.html")
        sys.exit(1)

    # Call Claude API
    client = anthropic.Anthropic(api_key=api_key)
    print(f"Calling Claude API to refresh content for {today}...")

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",   # Fast + cheap for automated refresh
        max_tokens=8192,
        messages=[{
            "role": "user",
            "content": build_prompt(today, trends_data, trends_html, whats_new_html),
        }],
    )

    response_text = message.content[0].text

    # Parse delimiter
    parts = response_text.split("---SECTION-BREAK---")
    if len(parts) != 2:
        print(f"ERROR: Expected 2 sections from Claude, got {len(parts)}. Raw response saved to debug_response.txt.")
        with open("debug_response.txt", "w", encoding="utf-8") as f:
            f.write(response_text)
        sys.exit(1)

    new_trends   = parts[0].strip()
    new_whats_new = parts[1].strip()

    # Validate the returned sections look like HTML
    for label, section in [("trends", new_trends), ("whats-new", new_whats_new)]:
        if not section.startswith("<section"):
            print(f"ERROR: Returned '{label}' section doesn't start with <section>. Aborting.")
            with open("debug_response.txt", "w", encoding="utf-8") as f:
                f.write(response_text)
            sys.exit(1)

    # Replace sections in the full HTML
    html = replace_section(html, "tab-trends",    new_trends)
    html = replace_section(html, "tab-whats-new", new_whats_new)

    # Verify closing tag still present (guard against truncation)
    if "</html>" not in html:
        print("ERROR: </html> missing after replacement — aborting to avoid corrupting the file.")
        sys.exit(1)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"index.html updated successfully with content dated {today}.")
    print(f"  Input tokens:  {message.usage.input_tokens}")
    print(f"  Output tokens: {message.usage.output_tokens}")


if __name__ == "__main__":
    main()
