"""Markdown → canonical source.md (validator / pass-through).

If your source is already a Markdown file with frontmatter, use this
to verify it's in the canonical shape and fill in any missing required
fields with reasonable defaults.

Usage:
    python adapters/from_markdown.py <input.md> > source.md
    python adapters/from_markdown.py <input.md> -o source.md \\
        --title "..." --kind notes
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path


REQUIRED = ("title", "date", "kind")


def _parse_frontmatter(raw: str) -> tuple[dict, str]:
    """Very small YAML-ish frontmatter parser. Returns (fm_dict, body)."""
    if not raw.startswith("---\n"):
        return {}, raw
    end = raw.find("\n---\n", 4)
    if end == -1:
        return {}, raw
    block = raw[4:end]
    body = raw[end + 5 :]
    fm: dict = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        fm[k.strip()] = v.strip().strip('"')
    return fm, body


def _yaml_escape(s: str) -> str:
    if s is None:
        return ""
    s = str(s).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'


def markdown_to_source(
    raw: str,
    override_title: str | None = None,
    override_kind: str | None = None,
    override_date: str | None = None,
) -> str:
    fm, body = _parse_frontmatter(raw)

    title = override_title or fm.get("title")
    if not title:
        # Fall back to first h1, else "Untitled"
        for line in body.splitlines():
            if line.strip().startswith("# "):
                title = line.strip()[2:].strip()
                break
        if not title:
            title = "Untitled"

    date = override_date or fm.get("date") or datetime.now().strftime("%Y-%m-%d")
    kind = override_kind or fm.get("kind") or "markdown"

    lines = ["---"]
    lines.append(f"title: {_yaml_escape(title)}")
    lines.append(f"date: {date}")
    lines.append(f"kind: {kind}")
    # Preserve any other frontmatter keys we recognize
    for k, v in fm.items():
        if k in ("title", "date", "kind"):
            continue
        lines.append(f"{k}: {_yaml_escape(v)}")
    lines.append("---")
    lines.append("")
    lines.append(body.lstrip("\n"))
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("markdown", type=Path, help="Input markdown file.")
    ap.add_argument("-o", "--output", type=Path, default=None)
    ap.add_argument("--title", default=None)
    ap.add_argument("--kind", default=None,
                    help="Override `kind` in frontmatter. Default: 'markdown' (or existing value).")
    ap.add_argument("--date", default=None)
    args = ap.parse_args()

    raw = args.markdown.read_text()
    out = markdown_to_source(
        raw,
        override_title=args.title,
        override_kind=args.kind,
        override_date=args.date,
    )
    if args.output:
        args.output.write_text(out)
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
