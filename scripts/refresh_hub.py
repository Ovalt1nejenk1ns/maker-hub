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


def clean_section(text: str) -> str:
    """
    Strip markdown code fences, leading/trailing whitespace, and any
    preamble or postamble around the actual <section>...</section> block.
    Handles responses like:
      - ```html\n<section>...</section>\n```
      - "Here is the updated section:\n\n<section>...</section>"
      - Plain <section>...</section>
    """
    # Remove opening ``` fence (with optional language tag)
    text = re.sub(r'^\s*```[^\n]*\n?', '', text, flags=re.MULTILINE)
    # Remove closing ``` fence
    text = re.sub(r'\n?```\s*$', '', text, flags=re.MULTILINE)
    text = text.strip()

    # Skip any preamble before the first <section tag
    idx = text.find('<section')
    if idx == -1:
        return text   # no <section found — caller's validation will catch this
    if idx > 0:
        text = text[idx:]

    # Trim anything after the final </section>
    end_idx = text.rfind('</section>')
    if end_idx != -1:
        text = text[:end_idx + len('</section>')]

    return text.strip()


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

## Fresh trend data

{json.dumps(trends_data, indent=2)}

---

## CURRENT TRENDS SECTION (id="tab-trends") — rewrite with fresh data

{trends_html}

---

## CURRENT WHAT'S NEW SECTION (id="tab-whats-new") — update date only

{whats_new_html}

---

## STRICT OUTPUT RULES — follow exactly

- Output RAW HTML only. Zero markdown. Zero code fences. Zero explanation text.
- First character of your response MUST be the < of the opening <section tag for the trends section.
- Separate the two sections with this exact delimiter on its own line: ---SECTION-BREAK---
- Last character of your response MUST be the > of the closing </section> tag for the whats-new section.
- Do not add anything before, between, or after the two sections.

## CONTENT RULES

1. TRENDS section: rewrite using the fresh data. Keep the EXACT same CSS classes and HTML structure already present. Update any "Trending —" header to "Trending — {today}". Include GitHub repos, Reddit posts (if any), and HN highlights.
2. WHAT'S NEW section: update ONLY the date / "last updated" text to {today}. Leave everything else unchanged.

Output format (raw HTML, nothing else):
<section ... id="tab-trends" ...> ... </section>
---SECTION-BREAK---
<section ... id="tab-whats-new" ...> ... </section>"""


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set.")
        sys.exit(1)

    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    with open("trends_data.json", "r", encoding="utf-8") as f:
        trends_data = json.load(f)

    today = datetime.now().strftime("%B %d, %Y")

    trends_html, _, _ = extract_section(html, "tab-trends")
    whats_new_html, _, _ = extract_section(html, "tab-whats-new")

    if not trends_html:
        print("ERROR: Could not find id='tab-trends' in index.html")
        sys.exit(1)
    if not whats_new_html:
        print("ERROR: Could not find id='tab-whats-new' in index.html")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    print(f"Calling Claude API to refresh content for {today}...")

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=8192,
        messages=[
            {
                "role": "user",
                "content": build_prompt(today, trends_data, trends_html, whats_new_html),
            },
            {
                # Prefill forces the response to start with <section — no preamble possible
                "role": "assistant",
                "content": "<section",
            },
        ],
    )

    # Re-attach the prefilled opening tag that we forced
    response_text = "<section" + message.content[0].text

    parts = response_text.split("---SECTION-BREAK---")
    if len(parts) != 2:
        print(f"ERROR: Expected 2 sections, got {len(parts)}. Saving debug_response.txt.")
        with open("debug_response.txt", "w", encoding="utf-8") as f:
            f.write(response_text)
        sys.exit(1)

    new_trends    = clean_section(parts[0])
    new_whats_new = clean_section(parts[1])

    for label, section in [("trends", new_trends), ("whats-new", new_whats_new)]:
        if not section.startswith("<section"):
            print(f"ERROR: '{label}' section doesn't start with <section after cleaning. Saving debug_response.txt.")
            with open("debug_response.txt", "w", encoding="utf-8") as f:
                f.write(response_text)
            sys.exit(1)

    html = replace_section(html, "tab-trends",    new_trends)
    html = replace_section(html, "tab-whats-new", new_whats_new)

    if "</html>" not in html:
        print("ERROR: </html> missing after replacement — aborting to avoid corrupting the file.")
        sys.exit(1)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"index.html updated successfully — {today}")
    print(f"  Input tokens:  {message.usage.input_tokens}")
    print(f"  Output tokens: {message.usage.output_tokens}")


if __name__ == "__main__":
    main()
