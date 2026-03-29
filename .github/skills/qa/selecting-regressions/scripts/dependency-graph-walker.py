#!/usr/bin/env python3
"""Walk dependency graph to find transitive dependencies.

Usage: echo '{"affected_files": [...], "dependency_graph": {...}}' | python dependency-graph-walker.py
Output: JSON with transitive affected modules.

Graceful degradation: If no graph available, returns directly affected only.
"""

import json
import sys
from collections import deque


def normalize_path(path: str) -> str:
    """Normalize paths for consistent lookup."""
    return path.lstrip('./').rstrip('/')


def walk_graph(affected: list, graph: dict, max_depth: int = 3) -> set:
    """BFS walk of dependency graph to find transitive dependencies."""
    if not graph:
        return set(affected)

    visited = set(affected)
    queue = deque(affected)
    depth = {node: 0 for node in affected}

    while queue:
        current = queue.popleft()
        current_depth = depth.get(current, 0)

        if current_depth >= max_depth:
            continue

        # Find modules that import current module
        dependents = graph.get(normalize_path(current), {}).get('imported_by', [])

        for dep in dependents:
            if dep not in visited:
                visited.add(dep)
                queue.append(dep)
                depth[dep] = current_depth + 1

    return visited


def main():
    data = json.load(sys.stdin)
    affected_files = data.get('directly_affected_files', [])
    dependency_graph = data.get('dependency_graph', {})

    if not dependency_graph:
        # No graph available, return directly affected
        output = {
            'transitive_affected': affected_files,
            'confidence': 'low',
            'note': 'No dependency graph available. Recommend full test suite.'
        }
    else:
        transitive = walk_graph(affected_files, dependency_graph)
        output = {
            'transitive_affected': sorted(list(transitive)),
            'direct_count': len(affected_files),
            'transitive_count': len(transitive),
            'confidence': 'high'
        }

    json.dump(output, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
