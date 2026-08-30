# Host-side mermaid.js renders `.mermaid` in the Page Body

A Version's Page Body is a Sphinx JSON-builder fragment, not a Sphinx HTML site, so Sphinx theme JS never arrives. We render Mermaid source in the hosting app from a **vendored** mermaid 11.12.1 UMD build (`mermaid.min.js`) served as Django static. We do not add `sphinxcontrib-mermaid` here, do not rewrite stored Page Body, and do not treat mermaid-language fences as diagrams.

## Status

accepted

## Considered Options

- **Host-side mermaid.js** (chosen): already-imported Versions work if the Page Body still has a `.mermaid` node. `sphinxcontrib-mermaid` `raw` emits `<pre class="mermaid">` (not `<div>`); we treat any element with class `mermaid`.
- **Build-time SVG/PNG** (`mermaid_output_format`): host stays dumb; every Project must rebuild and reimport. Rejected — we host fragments, we do not own Sphinx builds.
- **CDN mermaid (jsDelivr/cdnjs)**: matches MathJax's slot, but MathJax is on cdnjs; mermaid ESM is usually jsDelivr — a second script origin for CSP. Rejected. Vendor same-origin static instead.
- **Vendor `mermaid.min.js` 11.12.1** (chosen): `{% static %}` next to other app assets. Pin matches current `sphinxcontrib-mermaid` default. No SRI, no extra CSP host. Airgap works. Bump is a deliberate file replace.
- **Wrap `{% verbatim %}` at import**: protects `{{` from Django `Template()`, but stale Versions stay broken until reimport. Rejected.
- **Wrap `{% verbatim %}` at render** (chosen): in `SphinxPageBodyWidget`, **before** `Template()`, string-wrap each `<pre class="mermaid"…>` / `<div class="mermaid"…>` … matching close tag with `{% verbatim %}…{% endverbatim %}`. Do not parse the Page Body with lxml here — the string is HTML mixed with `{% load %}` / image tags. After `Template()`, `{{` is already gone. A diagram that contains the literal `{% endverbatim %}` can break the wrap; accept that.
- **Also render `language-mermaid` / `highlight-mermaid` fences**: Pygments HTML, not mermaid input. Rejected. Fences stay code. Only class `mermaid` is Mermaid source. Other Sphinx mermaid integrations that do not emit that class are out of scope.
- **Detect mermaid per page / follow dark theme / zoom / ELK**: extra code or extra vendor file (`@mermaid-js/layout-elk`) for no current requirement. Rejected. Cost: every view using `sphinx_hosting/base.html` downloads mermaid (same fat-JS bargain as MathJax). Elk layouts and Sphinx `mermaid_include_elk` fail until we vendor ELK. `theme: "neutral"` only; diagram YAML frontmatter may override. Wide diagrams: `.sphinxpage-body .mermaid { overflow-x: auto; }`.
- **Fix SVG `<object data>` rewrite**: `mermaid_output_format: svg` emits `<object>`, not `<img>`. Importer only remaps `img src`. Out of scope for this decision — host-side mermaid is the `raw` path. PNG `<img>` already follows the image map.

## Consequences

- Files: vendor `sphinx_hosting/static/sphinx_hosting/js/mermaid.min.js` (mermaid 11.12.1 UMD), load it from `sphinx_hosting/templates/sphinx_hosting/base.html` `extra_footer_js`, wrap in `sphinx_hosting/wildewidgets/sphinx_page.py`, overflow CSS in `sphinx_hosting/static/sphinx_hosting/css/sphinx_hosting.css`.
- Init: after the script, `mermaid.initialize({ startOnLoad: false, theme: "neutral" }); mermaid.run();`. Keep mermaid default `strict`. No `SPHINX_HOSTING_SETTINGS` key. No new Python package.
- Authors still need `sphinxcontrib-mermaid` (or anything that emits class `mermaid`) in their Sphinx **json** build. Host does not invent diagrams from code fences.
- Version skew: a Project built for another `mermaid_version` / elk / custom `mermaid_config` may not parse. Source stays visible. We do not sync host mermaid to each Version.
- Imported Page Body is trusted author HTML (same as today) plus a graph renderer. No extra sandbox. `{% endverbatim %}` inside a diagram is unsupported.
- SVG-as-`<object>` Versions stay broken until a separate importer change. Do not treat that as a mermaid.js bug.
