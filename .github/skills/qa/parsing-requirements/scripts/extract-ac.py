#!/usr/bin/env python3
"""Extract acceptance criteria from issue descriptions using regex + heuristics.

Usage: python extract-ac.py < issue_description.txt
Output: JSON array of {id, text, source} objects to stdout.

Supports formats:
- Markdown bullet lists under AC headers
- Given-When-Then blocks
- Numbered requirements
- JIRA-style "h3. Acceptance Criteria" sections
"""

import json
import re
import sys


def extract_ac_sections(text: str) -> list[str]:
    """Find sections likely to contain acceptance criteria."""
    patterns = [
        # Markdown headers
        r"(?:^|\n)#{1,3}\s*(?:acceptance\s+criteria|requirements|expected\s+behavior|ac)\s*\n([\s\S]*?)(?=\n#{1,3}\s|\Z)",
        # JIRA headers
        r"(?:^|\n)h[1-3]\.\s*(?:acceptance\s+criteria|requirements)\s*\n([\s\S]*?)(?=\nh[1-3]\.|\Z)",
    ]
    sections = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            sections.append(match.group(1).strip())
    return sections if sections else [text]


def extract_bullets(text: str) -> list[str]:
    """Extract bullet points and numbered items."""
    items = []
    for line in text.split("\n"):
        stripped = line.strip()
        # Markdown bullets: - item, * item, + item
        bullet_match = re.match(r"^[-*+]\s+(.+)$", stripped)
        if bullet_match:
            items.append(bullet_match.group(1).strip())
            continue
        # Numbered: 1. item, 1) item
        num_match = re.match(r"^\d+[.)]\s+(.+)$", stripped)
        if num_match:
            items.append(num_match.group(1).strip())
            continue
    return items


def extract_gwt(text: str) -> list[str]:
    """Extract Given-When-Then blocks as single AC strings."""
    pattern = r"(Given\s+.+?\s+When\s+.+?\s+Then\s+.+?)(?=\n\s*Given|\n\s*\n|\Z)"
    matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
    return [re.sub(r"\s+", " ", m).strip() for m in matches]


def deduplicate(items: list[str]) -> list[str]:
    """Remove near-duplicate items (case-insensitive)."""
    seen = set()
    result = []
    for item in items:
        normalized = item.lower().strip().rstrip(".")
        if normalized not in seen and len(normalized) > 5:
            seen.add(normalized)
            result.append(item)
    return result


def main():
    text = sys.stdin.read()
    if not text.strip():
        json.dump([], sys.stdout, indent=2)
        return

    all_items = []
    for section in extract_ac_sections(text):
        all_items.extend(extract_bullets(section))
        all_items.extend(extract_gwt(section))

    # Fallback: if no structured items found, split sentences
    if not all_items:
        sentences = re.split(r"[.!]\s+", text)
        all_items = [s.strip() for s in sentences if len(s.strip()) > 10]

    items = deduplicate(all_items)
    output = []
    for i, item in enumerate(items, 1):
        output.append({
            "id": f"AC-{i}",
            "text": item,
            "source": "gwt" if item.lower().startswith("given") else "bullet",
        })

    json.dump(output, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
