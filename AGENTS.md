# AGENTS.md

For LLM agents executing the pipeline.

## Your job

A human has run `python run.py --<input> <path>` and is pointing you
at the resulting `output/<date>-<slug>/` folder. Inside that folder
you'll find:

- `source.md` — the canonical input for this run.
- `_pipeline-snapshot/` — a frozen copy of the prompts, aesthetic,
  and config that this run is governed by.
- `NEXT.md` — your instruction sheet.

Read `NEXT.md`. It tells you which format prompt(s) to execute, in
what order, and which paths to substitute for each prompt's
`{{slots}}`.

## Prompt execution model

Each format under `_pipeline-snapshot/formats/<format>/prompt.md` is
written for you. It reads `source.md` (and for tweet-thread,
optionally a freshly-produced `blog.md` and `explainer-video.html` in
the same run folder) and produces one output file.

Execute prompts strictly in the order `NEXT.md` lists them, because:

- `tweet-thread` prefers to cite `blog.md` if it already exists.
- `tweet-thread` embeds `explainer-video.html` if the aesthetic's
  `format_specific.tweet-thread.pair_with_video` is true (it is by
  default).

## Aesthetic compliance

Each format prompt tells you to read the active aesthetic file and
internalize `voice.forbidden` / `voice.encouraged` before writing.
Take that seriously. It's the whole point of the pluggable layer.
Before returning a draft, walk it once against those lists and fix
any violations.

## Do not commit outputs

Outputs go in the run folder. The run folder is under `output/`,
which is gitignored. Do not `git add output/`. Do not suggest
committing blog drafts, tweet threads, or explainer videos. The
example under `examples/neural-computers/` is an intentionally-
committed golden; everything else stays local.

## Do not touch aesthetic/default.yaml

`aesthetic/default.yaml` is the shipped baseline for all users. If
you want to tune style, create or edit `aesthetic/<handle>.yaml`
(already gitignored) and point `config.yaml → active_aesthetic` at it.

## When something's ambiguous

- If `source.md` has thin frontmatter (no `claims`, no `citations`),
  the blog prompt still works; you just have less provenance to anchor.
- If the user asks for a format that isn't in `_pipeline-snapshot/formats/`,
  tell them to add a new format directory with a `prompt.md`, then rerun.
- If a prompt references a slot you can't fill (e.g. `{{blog_path}}`
  when blog wasn't generated this run), skip it gracefully.
