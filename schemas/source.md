# Canonical source format (`source.md`)

Every input to this pipeline is normalized to a single canonical form
before Stage 1 (draft blog) runs. The canonical form is a Markdown file
with YAML frontmatter.

Adapters (in [`../adapters/`](../adapters/)) convert format-specific
inputs into this shape. If your input is already a well-formatted
Markdown file with frontmatter, no adapter is required.

## Minimal required shape

```markdown
---
title: "A clear, specific title for the piece"
author: dmarz
date: 2026-04-23
kind: research_trace | transcript | notes | markdown | urls
---

# The body of the source material in Markdown.

Anything here is fair game. Stage 1 treats it as the substance the
author wants to turn into a blog post. The body should be rich enough
that a writing agent can extract a narrative arc, find claims to
anchor, and identify what's novel.
```

## Optional frontmatter fields

The richer your frontmatter, the better Stage 1 can work. None of these
are required; the writing agent will fall back to reasonable defaults.

```yaml
tldr: >
  1-2 sentences the author would say out loud to describe what this
  piece is about. Stage 1 uses this as the seed for the opening hook.

key_findings:
  - "First concrete, surprising finding the piece should communicate."
  - "Second finding."
  - "..."

citations:
  - url: https://example.com/paper
    title: "Source title"
    accessed: 2026-04-23
    role: primary | secondary | background

claims:
  - id: c1
    text: "A specific factual claim that must be defended in the post."
    confidence: 0.0 to 1.0
    sources: [url1, url2]
    reasoning: "Why the author believes this."

critique:
  verdict: "One-sentence summary of limitations."
  gaps:
    - "Something the source doesn't cover but the author knows matters."
  errors:
    - "Something that might be wrong and should be softened."

# Kind-specific metadata survives here, opaque to Stage 1 but readable
# by Stage 4 (review dashboard) for provenance display.
metadata:
  kind: research_trace
  trace_id: <uuid>
  tool_calls: <count>
  cost_usd: <number>
  ...
```

## Why this shape

- **Markdown body** is what every LLM is best at consuming and producing.
- **Frontmatter** carries machine-readable structure (citations, claims,
  critique) that Stages 2-5 can reference without reparsing the body.
- **`kind` tag** lets Stage 4 surface provenance appropriately (a
  research trace gets a different provenance panel than a transcript).
- **Open `metadata`** preserves adapter-specific detail without bloating
  the canonical surface.

## Supported input formats (today)

| format | adapter | typical source |
|---|---|---|
| **Research trace** (research-trace-v0.1 JSON) | [`adapters/from_research_trace.py`](../adapters/from_research_trace.py) | research-swarm runs (`runs/*.json`) |
| **VoxTerm transcript** (markdown w/ speakers) | [`adapters/from_voxterm.py`](../adapters/from_voxterm.py) | `~/Documents/voxterm-transcripts/*.md` |
| **Plain Markdown** (maybe with frontmatter) | [`adapters/from_markdown.py`](../adapters/from_markdown.py) | hand-written notes, existing drafts |

Add your own format by writing a new adapter that emits a `source.md`
and updating this table.
