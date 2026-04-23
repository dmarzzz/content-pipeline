"""content-pipeline run orchestrator.

The prompts themselves are LLM-executable (a coding-agent reads the
prompt file and follows its instructions). This script handles
everything around that: creating the run folder, materializing the
canonical source, pinning the aesthetic + prompts + config into a
per-run snapshot so reruns are reproducible, and printing exactly
what an agent should do next.

Usage:
    # From a research-swarm trace:
    python run.py --trace path/to/trace.json --slug neural-computers

    # From a voxterm transcript:
    python run.py --transcript ~/Documents/voxterm-transcripts/2026-04-22.md

    # From a plain markdown file:
    python run.py --markdown path/to/notes.md

    # Pick which formats to generate:
    python run.py --trace trace.json --formats blog,tweet-thread
    python run.py --trace trace.json --formats all

Outputs (under `output_root/<date>-<slug>/`):
    source.md                    canonical input
    _pipeline-snapshot/          frozen prompts + aesthetic + config
    NEXT.md                      instructions for the agent that will
                                 actually write the blog/thread/video
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path


PIPELINE_ROOT = Path(__file__).resolve().parent


def _slugify(s: str, max_len: int = 40) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return (s or "run")[:max_len]


# Defaults for the subset of config.yaml the orchestrator actually
# cares about. The LLM-executable prompts read config.yaml natively
# (YAML is a first-class format for them); this script only needs the
# three knobs below, so it hard-codes the defaults and supports CLI
# overrides. No YAML parsing, no dependencies.
_DEFAULT_CONFIG: dict = {
    "active_aesthetic": "aesthetic/default.yaml",
    "output_root": "output",
    "default_formats": ["explainer-video", "blog", "tweet-thread"],
}


def _load_config() -> dict:
    """Return orchestrator-level defaults. Prompts read `config.yaml`
    directly when they need to; this function intentionally does not
    parse it."""
    return dict(_DEFAULT_CONFIG)


def _run_adapter(
    kind: str, source_path: Path, out_path: Path, extra_args: list[str]
) -> None:
    """Invoke one of the adapter scripts to materialize source.md."""
    import subprocess

    adapter_map = {
        "trace": PIPELINE_ROOT / "adapters" / "from_research_trace.py",
        "transcript": PIPELINE_ROOT / "adapters" / "from_voxterm.py",
        "markdown": PIPELINE_ROOT / "adapters" / "from_markdown.py",
    }
    adapter = adapter_map[kind]
    cmd = [sys.executable, str(adapter), str(source_path), "-o", str(out_path)] + extra_args
    print(f"  ▸ {' '.join(cmd)}", file=sys.stderr)
    subprocess.check_call(cmd)


def _snapshot_pipeline(run_dir: Path, formats: list[str], aesthetic_path: Path) -> None:
    """Freeze the exact prompts + aesthetic + config used by this run."""
    snap = run_dir / "_pipeline-snapshot"
    snap.mkdir(exist_ok=True)
    # Config + active aesthetic
    shutil.copy(PIPELINE_ROOT / "config.yaml", snap / "config.yaml")
    (snap / "aesthetic").mkdir(exist_ok=True)
    shutil.copy(aesthetic_path, snap / "aesthetic" / aesthetic_path.name)
    # Prompts for each format this run will generate
    (snap / "formats").mkdir(exist_ok=True)
    for fmt in formats:
        src = PIPELINE_ROOT / "formats" / fmt
        if not src.exists():
            continue
        dst = snap / "formats" / fmt
        dst.mkdir(parents=True, exist_ok=True)
        for f in src.iterdir():
            if f.is_file():
                shutil.copy(f, dst / f.name)


def _write_next_md(run_dir: Path, source_path: Path, formats: list[str], aesthetic_path: Path) -> None:
    """Write a NEXT.md with copy-paste instructions the agent executes."""
    lines: list[str] = []
    lines.append(f"# next steps for run `{run_dir.name}`")
    lines.append("")
    lines.append("This run's canonical source and a frozen snapshot of the")
    lines.append("pipeline prompts + aesthetic are in this folder. An agent")
    lines.append("(Claude Code / Cursor / etc.) should now execute each format")
    lines.append("prompt below, in order, and write the output to this folder.")
    lines.append("")
    lines.append(f"- Source:     `{source_path.relative_to(run_dir)}`")
    lines.append(f"- Aesthetic:  `_pipeline-snapshot/aesthetic/{aesthetic_path.name}`")
    lines.append("")

    for fmt in formats:
        out_file = {
            "blog": "blog.md",
            "tweet-thread": "tweet-thread.md",
            "explainer-video": "explainer-video.html",
        }.get(fmt, f"{fmt}.out")
        prompt_path = f"_pipeline-snapshot/formats/{fmt}/prompt.md"
        lines.append(f"## format: {fmt}")
        lines.append("")
        lines.append(f"1. Read `{prompt_path}` end to end.")
        lines.append(f"2. Substitute these paths:")
        lines.append(f"   - `{{{{source_path}}}}` → `source.md`")
        lines.append(f"   - `{{{{aesthetic_path}}}}` → `_pipeline-snapshot/aesthetic/{aesthetic_path.name}`")
        lines.append(f"   - `{{{{output_path}}}}` → `{out_file}`")
        if fmt == "tweet-thread":
            lines.append(f"   - `{{{{blog_path}}}}` → `blog.md`       (if already generated)")
            lines.append(f"   - `{{{{video_path}}}}` → `explainer-video.html` (if already generated)")
        if fmt == "explainer-video":
            lines.append(f"   - `{{{{blog_path}}}}` → `blog.md`       (optional, may not exist)")
        lines.append(f"3. Follow the prompt's instructions; write the output to `{out_file}`.")
        lines.append("")

    (run_dir / "NEXT.md").write_text("\n".join(lines))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--trace", type=Path, help="research-trace-v0.1 JSON file")
    src.add_argument("--transcript", type=Path, help="VoxTerm transcript markdown file")
    src.add_argument("--markdown", type=Path, help="Plain markdown file (with or without frontmatter)")
    ap.add_argument("--slug", default=None, help="URL-safe slug for this run (default: derived from source title)")
    ap.add_argument("--formats", default=None,
                    help="Comma-separated list of formats or 'all' (default: from config.yaml)")
    ap.add_argument("--output-root", type=Path, default=None)
    args = ap.parse_args()

    cfg = _load_config()
    output_root = args.output_root or PIPELINE_ROOT / cfg.get("output_root", "output")
    active_aesthetic = PIPELINE_ROOT / cfg.get("active_aesthetic", "aesthetic/default.yaml")
    if not active_aesthetic.exists():
        print(f"error: active_aesthetic not found at {active_aesthetic}", file=sys.stderr)
        return 2

    # Resolve requested formats
    if args.formats:
        formats = [f.strip() for f in args.formats.split(",") if f.strip()]
        if formats == ["all"]:
            formats = ["explainer-video", "blog", "tweet-thread"]
    else:
        default = cfg.get("default_formats") or ["explainer-video", "blog", "tweet-thread"]
        formats = default if isinstance(default, list) else [default]
    valid = {"blog", "tweet-thread", "explainer-video"}
    unknown = [f for f in formats if f not in valid]
    if unknown:
        print(f"error: unknown format(s): {unknown}. Valid: {sorted(valid)}", file=sys.stderr)
        return 2

    # Create the run dir
    today = datetime.now().strftime("%Y-%m-%d")
    slug = args.slug or _slugify(
        (args.trace or args.transcript or args.markdown).stem
    )
    run_dir = output_root / f"{today}-{slug}"
    run_dir.mkdir(parents=True, exist_ok=True)

    # Materialize source.md via the right adapter
    source_path = run_dir / "source.md"
    print(f"▸ materializing source from "
          f"{'trace' if args.trace else 'transcript' if args.transcript else 'markdown'}", file=sys.stderr)
    if args.trace:
        _run_adapter("trace", args.trace, source_path, [])
    elif args.transcript:
        _run_adapter("transcript", args.transcript, source_path, [])
    else:
        _run_adapter("markdown", args.markdown, source_path, [])

    # Snapshot pipeline files + write NEXT.md
    print(f"▸ snapshotting pipeline source for this run", file=sys.stderr)
    _snapshot_pipeline(run_dir, formats, active_aesthetic)
    _write_next_md(run_dir, source_path, formats, active_aesthetic)

    print(f"\n✓ run ready at {run_dir}", file=sys.stderr)
    print(f"  formats: {', '.join(formats)}", file=sys.stderr)
    print(f"  aesthetic: {active_aesthetic.relative_to(PIPELINE_ROOT)}", file=sys.stderr)
    print(f"\n→ tell your agent to read {run_dir / 'NEXT.md'} and execute each format.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
