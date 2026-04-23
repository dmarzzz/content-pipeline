"""VoxTerm transcript → canonical source.md.

Converts a VoxTerm transcript markdown file (from
`~/Documents/voxterm-transcripts/*.md`) into the canonical `source.md`
format the pipeline consumes.

A VoxTerm transcript is a chronological conversation with speaker
labels. The adapter preserves the transcript body in the source
Markdown (so Stage 1 can quote directly) and extracts lightweight
metadata (speakers, duration) into frontmatter.

Usage:
    python adapters/from_voxterm.py <transcript.md> > source.md
    python adapters/from_voxterm.py <transcript.md> -o source.md \\
        --title "After-dinner jam on mixnets"
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path


SPEAKER_LINE = re.compile(r"^(?P<speaker>[A-Z][A-Za-z0-9_ .-]{0,40}):\s")


def _extract_speakers(body: str) -> list[str]:
    seen: list[str] = []
    for line in body.splitlines():
        m = SPEAKER_LINE.match(line.strip())
        if not m:
            continue
        name = m.group("speaker").strip()
        if name and name not in seen:
            seen.append(name)
    return seen


def _extract_existing_title(body: str) -> str | None:
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return None


def _yaml_escape(s: str) -> str:
    if s is None:
        return ""
    s = str(s).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'


def voxterm_to_source(
    raw: str,
    override_title: str | None = None,
    override_date: str | None = None,
) -> str:
    """Emit a canonical source.md string from a voxterm transcript."""
    # Split frontmatter (if any) from body.
    body = raw
    existing_fm: dict = {}
    if raw.startswith("---\n"):
        end = raw.find("\n---\n", 4)
        if end != -1:
            fm_block = raw[4:end]
            body = raw[end + 5 :]
            for line in fm_block.splitlines():
                if ":" not in line:
                    continue
                k, _, v = line.partition(":")
                existing_fm[k.strip()] = v.strip().strip('"')

    title = override_title or existing_fm.get("title") or _extract_existing_title(body) \
        or "VoxTerm session"
    date = override_date or existing_fm.get("date") \
        or datetime.now().strftime("%Y-%m-%d")
    speakers = _extract_speakers(body)

    lines = ["---"]
    lines.append(f"title: {_yaml_escape(title)}")
    lines.append(f"date: {date}")
    lines.append("kind: transcript")
    if speakers:
        lines.append("speakers:")
        for s in speakers:
            lines.append(f"  - {_yaml_escape(s)}")
    if existing_fm.get("duration"):
        lines.append(f"duration: {existing_fm['duration']}")
    lines.append("metadata:")
    lines.append("  kind: voxterm_transcript")
    if existing_fm:
        for k, v in existing_fm.items():
            if k in ("title", "date", "duration"):
                continue  # already lifted above
            lines.append(f"  {k}: {_yaml_escape(v)}")
    lines.append("---")
    lines.append("")

    # Body: include the full transcript. The writing agent will decide
    # what to quote vs. paraphrase. Strip an existing leading h1 since
    # we moved the title to frontmatter.
    body_lines = body.splitlines()
    while body_lines and (not body_lines[0].strip() or body_lines[0].strip().startswith("# ")):
        if body_lines[0].strip().startswith("# "):
            body_lines.pop(0)
            break
        body_lines.pop(0)
    lines.append("## Transcript")
    lines.append("")
    lines.extend(body_lines)
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("transcript", type=Path, help="Path to VoxTerm transcript markdown.")
    ap.add_argument("-o", "--output", type=Path, default=None,
                    help="Write to this path instead of stdout.")
    ap.add_argument("--title", default=None,
                    help="Override the title (otherwise taken from frontmatter or first h1).")
    ap.add_argument("--date", default=None,
                    help="Override the date (otherwise from frontmatter or today).")
    args = ap.parse_args()

    raw = args.transcript.read_text()
    out = voxterm_to_source(raw, override_title=args.title, override_date=args.date)
    if args.output:
        args.output.write_text(out)
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
