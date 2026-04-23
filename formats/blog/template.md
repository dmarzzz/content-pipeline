<!-- content-pipeline blog template
     Agents fill in {{slots}}; everything else is structural scaffolding
     they can adapt as needed. -->

---
title: {{title}}
date: {{date}}
source: {{source_path}}
aesthetic: {{aesthetic_path}}
generated_by: content-pipeline/formats/blog
---

{{opening_paragraph}}

{{shape_of_piece_paragraph}}

## {{section_1_heading}}

{{section_1_body}}

<details>
<summary>source</summary>

<source-citation>
  {{section_1_quote}}
  — <a href="{{section_1_url}}">{{section_1_title}}</a>
</source-citation>

<source-reasoning>
  {{section_1_reasoning}}
</source-reasoning>
</details>

<!-- Repeat ## section + <details> blocks for each arc beat -->

## Caveats & open questions

{{caveats_paragraph}}

{{closing_paragraph}}
