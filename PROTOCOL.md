# content-pipeline protocol

A small, opinionated pipeline that turns any well-structured source
into a trio of outputs: a blog post, a tweet thread, and an animated
explainer video. Inputs and outputs are both Markdown-first; the HTML
explainer video is a self-contained scrollytelling page.

## The shape

```
source (research trace | transcript | notes | markdown | anything)
        │
        ▼
   adapter ──→ source.md  (canonical: markdown body + YAML frontmatter)
                 │
                 ▼
    ┌────────────┼──────────────┐
    ▼            ▼              ▼
  formats/blog  formats/tweet-thread  formats/explainer-video
      │                │                       │
  blog.md        tweet-thread.md      explainer-video.html
```

Everything is driven by prompts an LLM-agent executes. The Python
`run.py` orchestrates the mechanics (materialize source, snapshot
pipeline source into the run folder, generate a NEXT.md that tells
the agent which prompt to execute in what order with what paths).

## Inputs: bring whatever you have

| input | adapter |
|---|---|
| research-swarm run (JSON) | `adapters/from_research_trace.py` |
| VoxTerm transcript | `adapters/from_voxterm.py` |
| hand-written markdown | `adapters/from_markdown.py` |

Each adapter emits the canonical [`source.md`](./schemas/source.md).
Add a new format by writing an adapter that also emits a valid
`source.md` and extending the table in
[`schemas/source.md`](./schemas/source.md).

## The source.md contract

Markdown body + YAML frontmatter. Minimum required frontmatter:

```yaml
---
title: ...
date: YYYY-MM-DD
kind: research_trace | transcript | notes | markdown | ...
---
```

Optional-but-valuable frontmatter fields (`tldr`, `key_findings`,
`citations`, `claims`, `critique`, `metadata`) let the format prompts
work harder. See [`schemas/source.md`](./schemas/source.md).

## Outputs

Every run lands in `output/<YYYY-MM-DD>-<slug>/`:

```
source.md                      canonical input used
blog.md                        if blog format ran
tweet-thread.md                if tweet-thread format ran
sketches.md                    if explainer-video format ran (sketch phase)
no-go.md                       if a format declined to produce an artifact
_decision.md                   user's chosen direction (created by user)
explainer-video.html           if explainer-video format ran (build phase)
build-skipped.md               if a build phase ran without prereqs
_pipeline-snapshot/            frozen prompts + aesthetic + config
  config.yaml                  so this run is reproducible even if you
  aesthetic/<name>.yaml        edit the main pipeline tomorrow
  formats/
    blog/prompt.md
    tweet-thread/prompt.md
    explainer-video/{sketch.md, prompt.md, template.html}
NEXT.md                        agent-readable instructions:
                               exactly which prompt to execute with
                               which paths, in what order
```

`output/` is gitignored; nothing from a real run leaks into a PR.

## Formats

Three today, pluggable:

- **blog** ([`formats/blog/`](./formats/blog/)) — dual-layer Markdown.
  Surface narrative reads straight through; collapsible `<details>`
  blocks carry provenance for skeptical readers.
- **tweet-thread** ([`formats/tweet-thread/`](./formats/tweet-thread/))
  — 6–12 tweets. Tweet 1 stands alone. If an approved explainer video
  was produced in the same run, the thread embeds it; otherwise it
  doesn't (pair_with_video defaults to false in v2).
- **explainer-video**
  ([`formats/explainer-video/`](./formats/explainer-video/)) — single
  sustained composition (typographic, single-image, generative-system,
  or data-driven). Self-contained HTML. **Sketch-then-build flow**:
  the format produces 2–3 prose sketches first, the user picks one,
  *then* the build phase generates the page. The format may also
  return a `no-go.md` if the source doesn't warrant a video.

Add a format by creating `formats/<name>/prompt.md` (and any template
files it needs), then editing `config.yaml → default_formats` if you
want it included in a default run. To opt the format into the
sketch-then-build gate, drop a `sketch.md` next to `prompt.md` —
`run.py` wires the two phases into `NEXT.md` automatically.

## Sketch-then-build

Some formats (currently `explainer-video`) produce a *sketch* before
they produce an *artifact*. The flow:

1. Run `formats/<format>/sketch.md`. It produces either `sketches.md`
   (2–3 prose directions, ~150 words each, each naming a single
   load-bearing visual claim and the things it deliberately omits)
   or `no-go.md` (a recommendation to skip the format because the
   source doesn't warrant it).
2. **Stop.** Present the sketches (or no-go) to the user.
3. The user records a choice in `_decision.md`:

   ```yaml
   ---
   chosen: A | B | C | none
   visual_claim: "<one sentence>"
   form: typographic-first | single-image | generative-system | data-driven
   notes: "<any user direction beyond the sketch>"
   ---
   ```

4. Run `formats/<format>/prompt.md`. It verifies `_decision.md`
   exists and refuses to run otherwise. If `chosen: none`, the
   format produces nothing; the no-go reasoning is the final
   artifact.

This gate exists because v1 generated visuals on autopilot and
shipped tasteless ones. Sketch-then-build separates the "what
should this be?" decision from the "make it" execution, so taste
failures get caught at the brief stage instead of in 500 lines of
HTML.

## Taste

The aesthetic file's `taste` section governs visual decisions:

- `taste.references` — work the user has approved as the right
  register. The sketch phase reads these; they are *never* cited on
  generated pages.
- `taste.anti_patterns` — moves forbidden by default
  (developer-doodle SVG, influence-cosplay, slideshow-of-panels,
  decorative typography doing unearned mood work, etc.).
- `taste.defaults` — default visual register, max metaphors per
  composition, the "earn each element" rule, and whether to escalate
  visual builds to the `frontend-design` subagent.

Override per-handle by adding `references` and softening
`anti_patterns` in your own `aesthetic/<handle>.yaml`.

## Aesthetic

All voice, style, length, and visual-identity knobs live in
[`aesthetic/`](./aesthetic/). [`aesthetic/default.yaml`](./aesthetic/default.yaml)
is the shipped neutral baseline. To use your own:

```bash
cp aesthetic/default.yaml aesthetic/your-handle.yaml
# edit aesthetic/your-handle.yaml to your voice / style
# set config.yaml → active_aesthetic: aesthetic/your-handle.yaml
```

Anything other than `default.yaml` in `aesthetic/` is gitignored so
your personal style doesn't leak to a PR.

## Running

```bash
# From a research trace:
python run.py --trace path/to/trace.json

# From a voxterm transcript:
python run.py --transcript ~/Documents/voxterm-transcripts/2026-04-22.md

# From any markdown file:
python run.py --markdown path/to/notes.md

# Pick formats:
python run.py --trace trace.json --formats blog,tweet-thread
python run.py --trace trace.json --formats all
```

`run.py` creates the run folder, materializes `source.md`, snapshots
the pipeline source, and writes `NEXT.md`. You then point your agent
(Claude Code, Cursor, etc.) at `NEXT.md` and it executes the prompts.

## Reproducibility

Every run folder contains a full frozen snapshot of the prompts,
aesthetic, and config that produced its outputs. Bumping the main
pipeline never invalidates old runs. If you want to regenerate an old
run against the new pipeline, delete the run folder and rerun;
otherwise the historical artifacts stay exactly as they were.
