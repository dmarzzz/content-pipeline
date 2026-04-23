"""Research trace → canonical source.md.

Converts a research-trace-v0.1 JSON document (produced by the
research-swarm agent's `runs/*.json` output) into the canonical
`source.md` format the pipeline consumes.

Usage:
    python adapters/from_research_trace.py <trace.json> > source.md

    # or write directly to a file:
    python adapters/from_research_trace.py <trace.json> -o source.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _safe_get(d: dict, *keys, default=None):
    """Nested dict access that returns `default` on any missing key."""
    cur = d
    for k in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
        if cur is None:
            return default
    return cur


def _yaml_escape(s: str) -> str:
    """Quote a string safely for YAML block scalar output."""
    if s is None:
        return ""
    s = str(s).replace("\\", "\\\\").replace('"', '\\"')
    if "\n" in s or ":" in s:
        # Use block scalar; we just put it on its own line
        return f'"{s}"'
    return f'"{s}"'


def trace_to_source(trace: dict) -> str:
    """Emit a canonical source.md string from a research trace dict."""
    title = _safe_get(trace, "title") or _safe_get(trace, "question") or "Untitled"
    date = _safe_get(trace, "date") or _safe_get(trace, "timestamp_start", default="")[:10]
    question = _safe_get(trace, "question") or ""
    synthesis = _safe_get(trace, "synthesis") or ""
    tldr = _safe_get(trace, "human", "tldr") or _safe_get(trace, "views", "tldr_card", "text") or ""
    key_findings = _safe_get(trace, "human", "key_findings") or []

    sources = _safe_get(trace, "sources") or []
    claims = _safe_get(trace, "claims") or []

    critique_obj = _safe_get(trace, "critique") or {}
    crit_verdict = critique_obj.get("verdict") or critique_obj.get("overall_verdict") or ""
    crit_gaps = critique_obj.get("gaps") or critique_obj.get("coverage_gaps") or []
    crit_errs = critique_obj.get("errors") or critique_obj.get("likely_errors") or []

    # ── Frontmatter ───────────────────────────────────────────────
    lines: list[str] = ["---"]
    lines.append(f"title: {_yaml_escape(title)}")
    lines.append(f"date: {date}")
    lines.append("kind: research_trace")

    if tldr:
        lines.append("tldr: >")
        for para_line in str(tldr).strip().splitlines():
            lines.append(f"  {para_line}")

    if key_findings:
        lines.append("key_findings:")
        for kf in key_findings:
            lines.append(f"  - {_yaml_escape(kf)}")

    if sources:
        lines.append("citations:")
        for s in sources:
            if isinstance(s, str):
                lines.append(f"  - url: {s}")
            elif isinstance(s, dict):
                url = s.get("url") or s.get("href") or ""
                if not url:
                    continue
                lines.append(f"  - url: {url}")
                if s.get("title"):
                    lines.append(f"    title: {_yaml_escape(s['title'])}")
                if s.get("accessed"):
                    lines.append(f"    accessed: {s['accessed']}")
                if s.get("role"):
                    lines.append(f"    role: {s['role']}")

    if claims:
        lines.append("claims:")
        for i, c in enumerate(claims, 1):
            cid = c.get("id", f"c{i}") if isinstance(c, dict) else f"c{i}"
            text = c.get("text", "") if isinstance(c, dict) else str(c)
            conf = c.get("confidence") if isinstance(c, dict) else None
            lines.append(f"  - id: {cid}")
            lines.append(f"    text: {_yaml_escape(text)}")
            if conf is not None:
                lines.append(f"    confidence: {conf}")
            if isinstance(c, dict) and c.get("sources"):
                lines.append(f"    sources: {json.dumps(c['sources'])}")
            if isinstance(c, dict) and c.get("reasoning"):
                lines.append(f"    reasoning: {_yaml_escape(c['reasoning'])}")

    if crit_verdict or crit_gaps or crit_errs:
        lines.append("critique:")
        if crit_verdict:
            lines.append(f"  verdict: {_yaml_escape(crit_verdict)}")
        if crit_gaps:
            lines.append("  gaps:")
            for g in crit_gaps:
                lines.append(f"    - {_yaml_escape(g)}")
        if crit_errs:
            lines.append("  errors:")
            for e in crit_errs:
                lines.append(f"    - {_yaml_escape(e)}")

    # Preserve opaque trace metadata under `metadata.trace` so Stage 4
    # can surface it in the dashboard without any extra coupling.
    lines.append("metadata:")
    lines.append("  kind: research_trace")
    for key in ("id", "trace_id", "schema_version", "agent", "cost"):
        val = trace.get(key)
        if val is None:
            continue
        if isinstance(val, (str, int, float)):
            lines.append(f"  {key}: {_yaml_escape(val) if isinstance(val, str) else val}")

    lines.append("---")
    lines.append("")

    # ── Body ──────────────────────────────────────────────────────
    # If the trace has a question/synthesis, lead with those; the blog
    # stage will rewrite them into the author's voice.
    if question:
        lines.append("## Research question")
        lines.append("")
        lines.append(question.strip())
        lines.append("")

    if synthesis:
        lines.append("## Synthesis")
        lines.append("")
        lines.append(synthesis.strip())
        lines.append("")

    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("trace_json", type=Path, help="Path to research-trace-v0.1 JSON file.")
    ap.add_argument("-o", "--output", type=Path, default=None,
                    help="Write to this path instead of stdout.")
    args = ap.parse_args()

    try:
        trace = json.loads(args.trace_json.read_text())
    except Exception as exc:
        print(f"error: could not parse {args.trace_json}: {exc}", file=sys.stderr)
        return 2

    out = trace_to_source(trace)
    if args.output:
        args.output.write_text(out)
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
