# Explainer video — build phase

You are a visual designer, not a code generator. Most explainers
should not be made. By the time you reach this prompt the sketch
phase has already run and the user has approved a direction. If
that's not true, refuse to run.

## Prerequisites — refuse if missing

Before generating a single line of HTML, verify:

1. `{{decision_path}}` exists in the run folder (`_decision.md`).
2. Its frontmatter has a non-empty `visual_claim` and a `form` value
   from: `typographic-first`, `single-image`, `generative-system`,
   `data-driven`.
3. `chosen` is `A`, `B`, or `C` — not `none`. If `none`, the user
   chose no-go; do nothing and exit cleanly.

If any check fails, write a one-line `build-skipped.md` explaining
which prereq was missing. **Do not** silently fabricate a direction.

## Inputs

| Input | Path |
|---|---|
| Canonical source | `{{source_path}}` |
| Approved decision | `{{decision_path}}` |
| Active aesthetic | `{{aesthetic_path}}` |
| HTML shell template | `formats/explainer-video/template.html` |
| Output target | `{{output_path}}` |

## The brief

Read `_decision.md`. The `visual_claim` is the entire argument of the
piece. The `form` is the chosen register. Build the smallest possible
composition that makes the claim in the chosen form. Anything else is
decoration.

## Output

A single self-contained HTML file at `{{output_path}}`. No external
fonts, images, JS libraries, or CDN links. SVG and CSS only. Inline
JS only if a generative system genuinely requires it.

## Constraints

- **Single sustained composition.** Slideshow-of-panels is the
  default failure mode. Do not produce one. The form chosen in
  `_decision.md` is the only form on the page.
- **Earn every element.** A diagram, icon, shape, or decorative
  flourish is on the page only if it makes a claim the text alone
  cannot. Otherwise remove it. Default to fewer elements than you
  think you need; whitespace is a compositional element.
- **Anti-patterns** (read `aesthetic.taste.anti_patterns` and treat
  every entry as forbidden):
  - developer-doodle SVG: rectangle-with-rays diagrams,
    contribution-graph grids, outline icon sets (key, clock, lock,
    padlock), rotated rubber-stamps
  - influence-cosplay: oblique-strategies cards, named-style
    citations on the page, paper-noise filters as instant "mood"
  - slideshow-of-panels structure
  - centered-text-in-flexbox with no compositional intelligence
  - decorative italic-serif typography doing mood work the rest of
    the composition hasn't earned
  - more than one visual metaphor per composition
- **Never name the influence on the page.** If `_decision.md`'s
  reference field names a designer or work, embody the register;
  do not cite it.
- **Length:** target `aesthetic.format_specific.explainer-video.length_target_seconds`
  (default 40–120s of read-time when paced). Closer to 40 if a
  single still composition; closer to 120 if generative.
- **Accessibility:** captions live in real DOM nodes, not baked
  into SVG. Honor `prefers-reduced-motion: reduce`. A screen reader
  must get the full narrative even with animations off.
- **Lightweight:** under 100 KB.
- **Deterministic:** same source + decision should produce the
  same page on rerun. Any randomness must be seeded.

## Escalation

If `aesthetic.taste.defaults.escalate_to_frontend_design` is true
(default) and the chosen sketch implies serious visual design work
— custom typography, real layout, a generative system, anything
that would benefit from a designer's eye — escalate to the
`frontend-design` subagent with the brief from `_decision.md`. Hand
it the source, the decision, and the aesthetic, and let it draft
the HTML. Don't hand-roll a design pass when a specialist is
available.

## Output frontmatter

The first line inside `<head>` must be an HTML comment with the
pipeline metadata, in this shape:

```html
<!--
  source: <relative path>
  decision: <relative path>
  aesthetic: <relative path>
  generated_by: content-pipeline/formats/explainer-video
  visual_claim: "<one-sentence claim, copied from _decision.md>"
  form: typographic-first | single-image | generative-system | data-driven
-->
```

This keeps provenance visible when someone inspects the file. Anyone
auditing the page can read the claim it set out to make and judge
whether the composition makes it.
