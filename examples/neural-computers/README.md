# example: neural-computers

A full worked run of the pipeline against a `research_trace`-kind
input. Good reference for what each format's output looks like when
the source is rich enough to anchor every claim.

## Layout

```
source.md                    canonical input, produced by
                             adapters/from_research_trace.py

outputs/
  blog.md                    blog format output (dual-layer)
  tweet-thread.md            tweet-thread format output
  review.html                pre-rewrite: legacy review dashboard
                             (kept as reference; new pipeline
                             produces explainer-video.html instead)
  visuals/                   animated HTML illustrations used by the
                             blog and referenced by the tweet thread

_pipeline-snapshot/          the exact prompts + aesthetic + config
  config.yaml                that produced these outputs. Never
  aesthetic-default.yaml     edit; re-run instead.
  formats/
    blog/
    tweet-thread/
    explainer-video/
```

## Reproducing this run

From the content-pipeline root:

```bash
# Materialize source.md from the trace JSON. You can use any trace; the
# one that produced these goldens lived at trace-to-post/examples/.
python run.py --trace <your-trace.json> --slug neural-computers

# The run orchestrator will create output/<date>-neural-computers/
# with source.md, _pipeline-snapshot/, and NEXT.md. Point your agent at
# NEXT.md to produce the format outputs.
```

## What to read first

1. `source.md` to see the canonical input shape.
2. `outputs/blog.md` to see what a dual-layer blog in the author's
   voice looks like.
3. `outputs/tweet-thread.md` to see how the thread compresses the blog.
4. `_pipeline-snapshot/formats/blog/prompt.md` to see the instructions
   that turned `source.md` into `outputs/blog.md`.
