#!/usr/bin/env python3
"""Analyze HTML and recommend stable, fragile selectors.

Usage:
  python selector-strategy.py --html page.html --output selectors.json

Output: JSON with recommended selectors, fragility scores, alternative strategies.
"""

import argparse
import json
import sys
from html.parser import HTMLParser


class InteractiveElementCollector(HTMLParser):
    """Extract interactive elements and their attributes."""

    def __init__(self) -> None:
        super().__init__()
        self.elements: list = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in ('button', 'a', 'input', 'select', 'textarea'):
            attr_dict = dict(attrs)
            self.elements.append({
                'tag': tag,
                'attrs': attr_dict,
                'text': '',
            })

    def handle_data(self, data: str) -> None:
        if self.elements and data.strip():
            self.elements[-1]['text'] += data.strip()


def analyze_selectors(html_content: str) -> list:
    """Analyze HTML and recommend selectors."""
    collector = InteractiveElementCollector()
    collector.feed(html_content)
    recommendations = []

    for elem in collector.elements:
        attrs = elem['attrs']
        tag = elem['tag']
        text = elem['text'][:50]

        rec: dict = {
            'element': tag,
            'text': text,
            'recommended': '',
            'alternatives': [],
            'stability_score': 0.5,
            'issues': [],
        }

        # Strategy 1: data-testid (most stable)
        data_testid = attrs.get('data-testid')
        if data_testid:
            rec['recommended'] = f'[data-testid="{data_testid}"]'
            rec['stability_score'] = 1.0
        else:
            rec['issues'].append('Missing data-testid (most stable selector)')

        # Strategy 2: aria-label
        aria_label = attrs.get('aria-label')
        if aria_label:
            rec['alternatives'].append(f'[aria-label="{aria_label}"]')
            if not rec['recommended']:
                rec['recommended'] = f'[aria-label="{aria_label}"]'
                rec['stability_score'] = 0.85

        # Strategy 3: id
        elem_id = attrs.get('id')
        if elem_id:
            rec['alternatives'].append(f'#{elem_id}')
            if not rec['recommended']:
                rec['recommended'] = f'#{elem_id}'
                rec['stability_score'] = 0.8

        # Strategy 4: class (moderate stability)
        class_attr = attrs.get('class', '')
        if class_attr:
            classes = class_attr.split()
            stable_classes = [c for c in classes if not c.startswith('_')]
            if stable_classes:
                css_selector = '.' + '.'.join(stable_classes[:2])
                rec['alternatives'].append(css_selector)
                if not rec['recommended']:
                    rec['recommended'] = css_selector
                    rec['stability_score'] = 0.7

        # Strategy 5: text content (fragile)
        if text and not rec['recommended']:
            xpath = f'//{tag}[contains(text(), "{text[:30]}")]'
            rec['alternatives'].append(xpath)
            rec['issues'].append(f'Text-based selector fragile if content changes: {text[:30]}')
            rec['recommended'] = xpath
            rec['stability_score'] = 0.4

        if not rec['recommended']:
            rec['recommended'] = tag
            rec['stability_score'] = 0.2
            rec['issues'].append('No stable selector found — add data-testid attribute')

        recommendations.append(rec)

    return recommendations


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze HTML and recommend selectors")
    parser.add_argument("--html", required=True, help="HTML file path")
    parser.add_argument("--output", default="selectors.json", help="Output JSON file")
    args = parser.parse_args()

    try:
        with open(args.html) as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"HTML file not found: {args.html}", file=sys.stderr)
        sys.exit(1)

    recommendations = analyze_selectors(html_content)

    audit = {
        "total_elements": len(recommendations),
        "with_data_testid": sum(1 for r in recommendations if 'data-testid' in r['recommended']),
        "with_issues": sum(1 for r in recommendations if r['issues']),
        "recommendations": recommendations,
    }

    with open(args.output, 'w') as f:
        json.dump(audit, f, indent=2)

    print(f"Analysis complete: {args.output}")


if __name__ == "__main__":
    main()
