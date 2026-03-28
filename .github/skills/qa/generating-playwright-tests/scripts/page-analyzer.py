#!/usr/bin/env python3
"""Parse page structure, extract interactive elements, group by section.

Usage:
  python page-analyzer.py --html page.html --output structure.json

Output: JSON with page sections, interactive elements, ARIA landmarks.
"""

import argparse
import json
import sys
from html.parser import HTMLParser


class PageStructureParser(HTMLParser):
    """Extract page structure: forms, interactive elements, landmarks."""

    def __init__(self) -> None:
        super().__init__()
        self.page_title = ""
        self.landmarks: list = []
        self.forms: list = []
        self.interactive_elements: list = []
        self._in_title = False
        self._current_form: dict = {}
        self._in_form = False

    def handle_starttag(self, tag: str, attrs: list) -> None:
        attr_dict = dict(attrs)

        if tag == 'title':
            self._in_title = True

        elif tag == 'form':
            self._current_form = {
                'action': attr_dict.get('action', ''),
                'method': attr_dict.get('method', 'GET'),
                'fields': [],
            }
            self._in_form = True

        elif tag in ('input', 'select', 'textarea') and self._in_form:
            self._current_form['fields'].append({
                'name': attr_dict.get('name', ''),
                'type': attr_dict.get('type', 'text'),
                'required': 'required' in attr_dict,
            })

        elif tag in ('nav', 'main', 'footer', 'header') or attr_dict.get('role'):
            role = attr_dict.get('role') or tag
            self.landmarks.append({'role': role, 'tag': tag})

        elif tag in ('button', 'a') or (tag == 'input' and attr_dict.get('type') == 'submit'):
            self.interactive_elements.append({
                'tag': tag,
                'type': attr_dict.get('type', 'button'),
                'data-testid': attr_dict.get('data-testid', ''),
                'aria-label': attr_dict.get('aria-label', ''),
                'text': '',
            })

    def handle_endtag(self, tag: str) -> None:
        if tag == 'title':
            self._in_title = False
        elif tag == 'form':
            self.forms.append(self._current_form)
            self._current_form = {}
            self._in_form = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.page_title += data
        elif self.interactive_elements and data.strip():
            self.interactive_elements[-1]['text'] += data.strip()[:50]


def analyze_page_structure(html_content: str) -> dict:
    """Extract page structure: headers, nav, sections, forms."""
    parser = PageStructureParser()
    parser.feed(html_content)

    return {
        "page_title": parser.page_title.strip(),
        "landmarks": parser.landmarks,
        "forms": parser.forms,
        "interactive_elements": parser.interactive_elements,
        "sections": [],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze page structure")
    parser.add_argument("--html", required=True, help="HTML file path")
    parser.add_argument("--output", default="structure.json", help="Output JSON file")
    args = parser.parse_args()

    try:
        with open(args.html) as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"HTML file not found: {args.html}", file=sys.stderr)
        sys.exit(1)

    structure = analyze_page_structure(html_content)

    with open(args.output, 'w') as f:
        json.dump(structure, f, indent=2)

    print(f"Structure analysis complete: {args.output}")


if __name__ == "__main__":
    main()
