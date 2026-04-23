# content-pipeline

Turns any well-structured source into a blog post, a tweet thread, and
an animated explainer video. Pluggable formats. Pluggable aesthetic.
Reproducible runs.

```bash
# research-swarm trace:
python run.py --trace path/to/trace.json

# voxterm transcript:
python run.py --transcript ~/Documents/voxterm-transcripts/2026-04-22.md

# any markdown file:
python run.py --markdown path/to/notes.md
```

Each run creates `output/<date>-<slug>/` with a canonical `source.md`,
a frozen `_pipeline-snapshot/` of the prompts + aesthetic used, and a
`NEXT.md` your coding agent follows to produce the format outputs.

## What ships

| directory | what |
|---|---|
| [`adapters/`](./adapters) | one script per input format → canonical `source.md` |
| [`schemas/source.md`](./schemas/source.md) | the canonical input contract |
| [`aesthetic/default.yaml`](./aesthetic/default.yaml) | default voice / style. Fork it to your handle. |
| [`formats/blog/`](./formats/blog) | dual-layer markdown blog prompt + template |
| [`formats/tweet-thread/`](./formats/tweet-thread) | 6-12 tweet distribution thread prompt |
| [`formats/explainer-video/`](./formats/explainer-video) | self-contained scrollytelling HTML prompt + template |
| [`examples/neural-computers/`](./examples/neural-computers) | one end-to-end worked run with goldens |

## Full protocol

See [`PROTOCOL.md`](./PROTOCOL.md) for the shape, reproducibility
guarantees, and how to add formats / adapters / aesthetics.

## What's gitignored

- `output/` — every runtime output. Blogs, threads, videos, snapshots.
- `aesthetic/*.yaml` except `default.yaml` — your personal voice file
  stays local unless you consciously commit it.

So you can iterate freely and never leak a half-cooked draft or a
personal style override into a pull request.
