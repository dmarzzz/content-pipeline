# AGENTS.md

For LLM agents executing the pipeline.

## Your job

A human runs `python3 run.py --<input> <path>` and points you at the
resulting `output/<date>-<slug>/` folder. Read `NEXT.md`. It tells
you which format prompts to execute, in what order, with which paths
to substitute for each prompt's `{{slot}}`.

Each format under `_pipeline-snapshot/formats/<format>/` is written
for you to execute against `source.md`. Write outputs to the run
folder. Outputs stay local.

## Sketch-then-build (explainer-video)

The `explainer-video` format has two phases. They run in order:

1. **Sketch.** Read and execute
   `_pipeline-snapshot/formats/explainer-video/sketch.md`. It produces
   either `sketches.md` (2–3 directions) or `no-go.md` (a
   recommendation to skip the format) in the run folder. After
   producing one of those files, **stop.** Present it to the user.
   Do not continue.

2. **Build.** Once the user has recorded a choice in `_decision.md`,
   read and execute
   `_pipeline-snapshot/formats/explainer-video/prompt.md`. It refuses
   to run without `_decision.md`.

If the user picks `none`, the format is done — no HTML gets
generated, the no-go reasoning carries through to `_decision.md`.

The `blog` and `tweet-thread` formats run straight through. Their
content-anchored discipline (dual-layer structure, tweet-1-stands-
alone) substitutes for a sketch gate by default. If a future format
needs a sketch phase, drop a `sketch.md` next to its `prompt.md` and
`run.py` will wire it into NEXT.md automatically.

## No-go is a valid completion

Any format may legitimately produce a no-go file instead of an
artifact. A no-go is not a failure. Record the reason; do not
generate a weak artifact to fill the slot. Examples:

- `sketches.md` → produced 2 directions, both clear
- `no-go.md` → "the argument is text-shaped; a video would be
  decoration"
- `build-skipped.md` → "build phase ran without `_decision.md`;
  refused per prereq"

## Aesthetic compliance

Each format prompt tells you to read the active aesthetic. Internalize:

- `voice.forbidden` / `voice.encouraged` — applies to all prose.
  Walk drafts against both lists before returning.
- `taste.references` — work the user has approved as the right
  register. Read these before sketching. **Embody, don't tag.**
  Never name a reference on a generated page.
- `taste.anti_patterns` — moves that are forbidden by default. The
  sketch phase audits each direction against this list. The build
  phase enforces it.
- `taste.defaults` — default visual register, max metaphors per
  composition, the "earn each element" rule, and whether to
  escalate to the `frontend-design` subagent.

## Escalation to frontend-design

When `taste.defaults.escalate_to_frontend_design` is true (default)
and the chosen sketch implies serious visual design work — custom
typography, real layout, a generative system, anything a specialist
would do better — hand the build off to the `frontend-design`
subagent. Brief it with `_decision.md`, `source.md`, and the
aesthetic file. Don't hand-roll a design pass when a specialist is
available.

## Do not commit outputs

Outputs go in the run folder, which is under `output/` (gitignored).
Do not `git add output/`. Do not suggest committing blog drafts,
tweet threads, or explainer videos.

The example under `examples/neural-computers/` is an intentionally-
committed golden; everything else stays local.

To host an artifact publicly, copy the specific file (not the run
folder) to `docs/explainers/<slug>.<ext>` — GitHub Pages serves
that directory. `output/` itself remains gitignored.

## Do not touch aesthetic/default.yaml for personal taste

`aesthetic/default.yaml` is the shipped baseline. To tune voice or
visuals to a personal aesthetic, create `aesthetic/<handle>.yaml`
(already gitignored) and point `config.yaml → active_aesthetic` at
it. Pipeline-level updates to `default.yaml` (rules everyone should
inherit) are fine; personal style overrides are not.

## When something's ambiguous

- Thin frontmatter on `source.md` (no `claims`, no `citations`):
  blog still works, you just have less provenance to anchor.
- Format not in `_pipeline-snapshot/formats/`: tell the user to add
  a new format directory with a `prompt.md`, then rerun.
- Slot you can't fill (e.g. `{{blog_path}}` when blog wasn't
  generated): skip gracefully.
- `_decision.md` missing for explainer-video build: write
  `build-skipped.md` and stop. Don't fabricate a direction.
