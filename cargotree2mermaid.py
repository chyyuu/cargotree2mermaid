#!/usr/bin/env python3
import argparse
import re
import sys


TREE_LINE_RE = re.compile(
    r'^(?P<prefix>(?:│   |    )*)(?:(?:├──|└──)\s)(?P<rest>.+)$'
)
SECTION_LINE_RE = re.compile(
    r'^(?P<prefix>(?:│   |    )*)(?P<section>\[[^\]]+\])\s*$'
)


def _sanitize_node_id(label):
    node_id = re.sub(r'[^0-9A-Za-z_]', '_', label)
    if node_id and node_id[0].isdigit():
        node_id = f"n_{node_id}"
    return node_id


def _parse_line(line):
    raw = line.rstrip("\n")
    if not raw.strip():
        return None
    match = TREE_LINE_RE.match(raw)
    if match:
        depth = len(match.group("prefix")) // 4 + 1
        payload = match.group("rest").strip()
        return depth, payload

    match = SECTION_LINE_RE.match(raw)
    if match:
        depth = len(match.group("prefix")) // 4 + 1
        payload = match.group("section").strip()
        return depth, payload

    if raw.lstrip().startswith(("│", "├", "└")):
        return None

    else:
        depth = 0
        payload = raw.strip()
        return depth, payload


def _parse_node(payload):
    if payload.startswith("["):
        return {
            "id": _sanitize_node_id(payload),
            "label": payload,
            "is_crate": False,
        }
    tokens = payload.split()
    if not tokens:
        return None
    name = tokens[0]
    version = tokens[1] if len(tokens) > 1 and tokens[1].startswith("v") else None
    label = f"{name} {version}" if version else name
    return {
        "id": _sanitize_node_id(label),
        "label": label,
        "is_crate": True,
    }


def parse_cargo_tree(lines, blacklist):
    """解析Cargo依赖树，提取依赖关系"""
    stack = []  # 每一层的节点信息
    dependencies = []
    seen = set()
    nodes = {}
    crates = set()

    for line in lines:
        parsed = _parse_line(line)
        if parsed is None:
            continue
        depth, payload = parsed
        node = _parse_node(payload)
        if node is None:
            continue

        if depth <= len(stack):
            stack = stack[:depth]

        if node["is_crate"]:
            crate_name = node["label"].split()[0]
            crates.add(crate_name)
            if crate_name in blacklist:
                stack.append(node)
                continue
            parent = None
            for ancestor in reversed(stack):
                if ancestor["is_crate"]:
                    if ancestor["label"].split()[0] in blacklist:
                        continue
                    parent = ancestor
                    break
            if parent is not None:
                edge = (parent["id"], node["id"])
                if edge not in seen:
                    seen.add(edge)
                    dependencies.append(edge)

        nodes.setdefault(node["id"], node["label"])
        stack.append(node)

    return dependencies, nodes, crates


def _read_input_lines(input_path):
    if input_path and input_path != "-":
        with open(input_path, "r", encoding="utf-8") as f:
            return f.readlines()
    return sys.stdin.read().splitlines(keepends=True)

def main():
    parser = argparse.ArgumentParser(
        description="Convert cargo tree output to a Mermaid dependency graph"
    )
    parser.add_argument(
        "-i",
        "--input",
        default=None,
        help="Path to cargo tree output file; use '-' or omit to read from stdin",
    )
    parser.add_argument(
        "-b",
        "--blacklist",
        default=None,
        help="Blacklist file path; crate names separated by commas or whitespace",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Mermaid output file path; print to screen if not provided",
    )
    parser.add_argument(
        "-w",
        "--white",
        default=None,
        help="Whitelist output file path; crates in cargo tree but not in blacklist",
    )
    parser.add_argument(
        "--direction",
        default="TD",
        choices=["TD", "TB", "LR", "RL", "BT"],
        help="Mermaid graph direction",
    )
    args = parser.parse_args()

    lines = _read_input_lines(args.input)

    blacklist = set()
    if args.blacklist:
        with open(args.blacklist, "r", encoding="utf-8") as f:
            content = f.read()
        items = re.split(r"[,\s]+", content.strip())
        for item in items:
            if not item:
                continue
            blacklist.add(item)
            if "_" in item:
                blacklist.add(item.replace("_", "-"))
            if "-" in item:
                blacklist.add(item.replace("-", "_"))

    dependencies, nodes, crates = parse_cargo_tree(lines, blacklist)

    mermaid_lines = [f"graph {args.direction}"]
    for parent, child in dependencies:
        mermaid_lines.append(
            f"    {parent}[{nodes[parent]}] --> {child}[{nodes[child]}]"
        )

    output_text = "\n".join(mermaid_lines) + "\n"
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_text)
    else:
        print(output_text, end="")

    if args.white:
        used_node_ids = set()
        for parent, child in dependencies:
            used_node_ids.add(parent)
            used_node_ids.add(child)
        whitelist = sorted(
            {
                nodes[node_id].split()[0]
                for node_id in used_node_ids
                if node_id in nodes
            }
        )
        with open(args.white, "w", encoding="utf-8") as f:
            f.write("\n".join(whitelist) + "\n")

    if args.output:
        print(f"Done! Dependency graph saved to {args.output}")

if __name__ == "__main__":
    main()
