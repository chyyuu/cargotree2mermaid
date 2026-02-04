#!/usr/bin/env python3
import argparse
import re
import sys


EDGE_LINE_RE = re.compile(r"^\s*(\S+)\[(.+?)\]\s*-->\s*(\S+)\[(.+?)\]\s*$")


def parse_mermaid_edges(lines):
    """Parse Mermaid graph and extract nodes and edges"""
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
    """Extract name from label (e.g., 'kernel-alloc v0.1.0' -> 'kernel-alloc')"""
    return label.split()[0] if label else label


def find_node_id_by_name(nodes, name):
    """Find node ID by crate name (case-insensitive, handle - and _)"""
    name_normalized = name.replace("_", "-").lower()
    
    for node_id, label in nodes.items():
        node_name = label_to_name(label)
        node_name_normalized = node_name.replace("_", "-").lower()
        if node_name_normalized == name_normalized:
            return node_id
    
    return None


def collect_downstream_deps(node_id, edges, nodes):
    """Collect all downstream dependencies (nodes that this node depends on)"""
    downstream = set()
    visited = set()
    queue = [node_id]
    
    while queue:
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)
        
        # Find children of current node
        for parent, child in edges:
            if parent == current and child not in visited:
                downstream.add(child)
                queue.append(child)
    
    return downstream


def collect_upstream_deps(node_id, edges, nodes):
    """Collect all upstream dependencies (nodes that depend on this node)"""
    upstream = set()
    visited = set()
    queue = [node_id]
    
    while queue:
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)
        
        # Find parents of current node
        for parent, child in edges:
            if child == current and parent not in visited:
                upstream.add(parent)
                queue.append(parent)
    
    return upstream


def extract_subgraph_edges(target_nodes, edges):
    """Extract edges that involve only the target nodes"""
    result_edges = []
    for parent, child in edges:
        if parent in target_nodes and child in target_nodes:
            result_edges.append((parent, child))
    return result_edges


def _read_input_lines(input_path):
    """Read input from file or stdin"""
    if input_path and input_path != "-":
        with open(input_path, "r", encoding="utf-8") as f:
            return f.readlines()
    return sys.stdin.read().splitlines(keepends=True)


def main():
    parser = argparse.ArgumentParser(
        description="Extract dependency subgraph for a specific node from Mermaid graph"
    )
    parser.add_argument(
        "-i",
        "--input",
        default=None,
        help="Mermaid dependency graph file path; use '-' or omit to read from stdin",
    )
    parser.add_argument(
        "-n",
        "--node",
        required=True,
        help="Node name to query (crate name)",
    )
    direction_group = parser.add_mutually_exclusive_group(required=True)
    direction_group.add_argument(
        "-u",
        "--up",
        action="store_true",
        help="Upward dependencies (nodes that depend on this node)",
    )
    direction_group.add_argument(
        "-d",
        "--down",
        action="store_true",
        help="Downward dependencies (nodes that this node depends on)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output file path; print to screen if not provided",
    )
    args = parser.parse_args()

    lines = _read_input_lines(args.input)
    nodes, edges = parse_mermaid_edges(lines)

    # Find the target node ID
    target_node_id = find_node_id_by_name(nodes, args.node)
    if target_node_id is None:
        raise SystemExit(f"Node '{args.node}' not found in graph")

    # Collect dependencies in the specified direction
    if args.up:
        target_nodes = collect_upstream_deps(target_node_id, edges, nodes)
    else:  # args.down
        target_nodes = collect_downstream_deps(target_node_id, edges, nodes)

    # Always include the target node itself
    target_nodes.add(target_node_id)

    # Extract edges that involve only target nodes
    subgraph_edges = extract_subgraph_edges(target_nodes, edges)

    # Generate Mermaid output
    mermaid_lines = ["graph TD"]
    for parent, child in subgraph_edges:
        mermaid_lines.append(
            f"    {parent}[{nodes[parent]}] --> {child}[{nodes[child]}]"
        )

    output_text = "\n".join(mermaid_lines) + "\n"

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_text)
        print(f"Node dependency graph saved to {args.output}")
    else:
        print(output_text, end="")


if __name__ == "__main__":
    main()
