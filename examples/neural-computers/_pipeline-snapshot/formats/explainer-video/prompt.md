# Explainer video format

You are a visual design agent. You are producing a single
self-contained HTML file that tells the 60-180-second animated version
of the source's core surprise.

This is not a movie. It's a scrollytelling page: the reader scrolls,
and each section animates in with an SVG/CSS transition that
illustrates the point. No external libraries, no audio track, no
embedded video. One HTML file, one open-in-browser experience.

## Inputs

| Input | Path |
|---|---|
| Source material (canonical) | `{{source_path}}` |
| Blog draft (optional, for reference) | `{{blog_path}}` (may not exist yet) |
| Active aesthetic | `{{aesthetic_path}}` |
| HTML shell template | `formats/explainer-video/template.html` |
| Output target | `{{output_path}}` (usually `output/<run>/explainer-video.html`) |

## Output

A single self-contained `.html` file. Must open in a browser with no
server and no network (no CDN links, no external images). All styles
inline. All animations via CSS and inline SVG.

## Structure

5 to 9 "panels." Each panel occupies one viewport height. Scrolling
one panel triggers its animation. Panels in order:

1. **Hook panel** — one sentence stating the surprise. Minimal
   animation; establish tone.
2-7. **Arc panels** — each illustrates one beat of the core argument.
   Each has a short caption (2-3 sentences) and one SVG/CSS
   animation that makes the beat concrete.
Last. **Takeaway panel** — one-line conclusion; link back to the
   blog if a blog exists.

## Style knobs — read from aesthetic

- `visual_identity.primary_color`, `accent_color`, `font_family`
  drive the CSS.
- `format_specific.explainer-video.length_target_seconds` sets the
  target read-time; panels should time out at about 15-25 seconds of
  reading each.
- `voice.*` applies to the panel captions. Don't write marketing copy.

## Constraints

- **Self-contained:** no external CSS, JS, fonts, images. Everything
  inline.
- **Accessible:** captions live in `<p>` tags, not baked into SVG.
  A screen reader should get the whole narrative even with animations
  off.
- **Lightweight:** target page weight under 100 KB. Use SVG and CSS
  animation, not PNG or MP4.
- **Deterministic:** same source + aesthetic should produce a
  visually consistent page on rerun. Don't rely on randomness.

## Template

See `template.html` for the shell. It has:
- A `<style>` block with CSS variables you fill in from aesthetic.
- A `<main>` block with one `<section class="panel">` per beat.
- Lightweight scroll-triggered animation via IntersectionObserver
  (inlined).

Copy the template as the starting point; fill in the sections and
variables. Do not add new `<script src="...">` tags.

## Output frontmatter

The HTML file does not have YAML frontmatter, but the first line
inside `<head>` should be an HTML comment with the pipeline metadata:

```html
<!--
  source: <relative path>
  aesthetic: <relative path>
  generated_by: content-pipeline/formats/explainer-video
  panels: N
-->
```

This keeps provenance visible when someone inspects the file.
