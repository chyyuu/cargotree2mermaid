#!/usr/bin/env python3
import argparse
import os
import re
from collections import deque


EDGE_LINE_RE = re.compile(r"^\s*(\S+)\[(.+?)\]\s*-->\s*(\S+)\[(.+?)\]\s*$")


def parse_mermaid_edges(lines):
    nodes = {}
    edges = []

    for line in lines:
        raw = line.strip()
        if not raw or raw.startswith("graph "):
            continue
        match = EDGE_LINE_RE.match(raw)
        if not match:
            continue
        parent_id, parent_label, child_id, child_label = match.groups()
        nodes.setdefault(parent_id, parent_label)
        nodes.setdefault(child_id, child_label)
        edges.append((parent_id, child_id))

    return nodes, edges


def label_to_name(label):
    return label.split()[0] if label else label


def compute_levels(nodes, edges, direction):
    adjacency = {node_id: set() for node_id in nodes}
    incoming = {node_id: 0 for node_id in nodes}

    if direction == "down":
        edges = [(child, parent) for parent, child in edges]

    for parent, child in edges:
        adjacency.setdefault(parent, set()).add(child)
        incoming[child] = incoming.get(child, 0) + 1
        incoming.setdefault(parent, incoming.get(parent, 0))

    roots = [node_id for node_id, count in incoming.items() if count == 0]
    if not roots:
        roots = list(nodes.keys())

    distances = {}
    queue = deque()
    for root in roots:
        distances[root] = 0
        queue.append(root)

    while queue:
        current = queue.popleft()
        next_distance = distances[current] + 1
        for child in adjacency.get(current, []):
            if child not in distances or next_distance < distances[child]:
                distances[child] = next_distance
                queue.append(child)

    return distances


def default_output_path(input_path, level, direction):
    base, _ = os.path.splitext(input_path)
    return f"{base}.{direction}.level{level}.txt"


def main():
    parser = argparse.ArgumentParser(
        description="Extract node list at a specific dependency level from Mermaid graph"
    )
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Mermaid dependency graph file path",
    )
    parser.add_argument(
        "-n",
        "--level",
        type=int,
        required=True,
        help="Dependency level (NUM >= 0)",
    )
    direction_group = parser.add_mutually_exclusive_group(required=True)
    direction_group.add_argument(
        "-u",
        "--up",
        action="store_true",
        help="Upward dependency level (default direction)",
    )
    direction_group.add_argument(
        "-d",
        "--down",
        action="store_true",
        help="Downward dependency level (reversed direction)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output file path; print to screen if not provided",
    )
    args = parser.parse_args()

    if args.level < 0:
        raise SystemExit("NUM must be >= 0")

    with open(args.input, "r", encoding="utf-8") as f:
        lines = f.readlines()

    nodes, edges = parse_mermaid_edges(lines)
    direction = "down" if args.down else "up"
    distances = compute_levels(nodes, edges, direction)

    name_map = {node_id: label_to_name(label) for node_id, label in nodes.items()}
    dependency_map = {}
    for parent, child in edges:
        dependency_map.setdefault(parent, set()).add(child)

    level_node_ids = [node_id for node_id in nodes if distances.get(node_id) == args.level]
    level_node_ids.sort(key=lambda node_id: name_map.get(node_id, ""))
    level_nodes = []
    for node_id in level_node_ids:
        deps = sorted(name_map.get(dep_id, dep_id) for dep_id in dependency_map.get(node_id, []))
        deps_text = ", ".join(deps)
        level_nodes.append(f"{name_map.get(node_id, node_id)}  :   {deps_text}")

    output_text = "\n".join(level_nodes) + "\n"

    if args.output:
        output_path = args.output
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output_text)
        print(f"Level {args.level} node list saved to {output_path}")
    else:
        print(output_text, end="")


if __name__ == "__main__":
    main()
