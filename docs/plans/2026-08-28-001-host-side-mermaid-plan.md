# Host-side mermaid Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Render Sphinx `raw` mermaid (class `mermaid`) in hosted Page Bodies using vendored mermaid 11.12.1, without rewriting stored HTML.

**Architecture:** A pure function wraps `.mermaid` blocks in `{% verbatim %}` on the Page Body string before Django `Template()` in `SphinxPageBodyWidget`. `base.html` loads vendored UMD `mermaid.min.js` and calls `mermaid.run()`. Overflow CSS lives in the existing page-body stylesheet. No importer change, no Python dependency, no `SPHINX_HOSTING_SETTINGS` key.

**Tech Stack:** Django templates, wildewidgets `SphinxPageBodyWidget`, mermaid 11.12.1 UMD, pytest in the `demo` container.

**Spec:** `docs/adr/0002-host-side-mermaid.md`. Glossary: `CONTEXT.md` (**Page Body**, **Mermaid source**).

## Global Constraints

- Mermaid source is class token `mermaid` only (`<pre>` or `<div>`). Do not wrap `highlight-mermaid` / `language-mermaid`.
- Do not parse Page Body with lxml at render (HTML mixed with `{%` image tags).
- Vendor `mermaid@11.12.1` `dist/mermaid.min.js` unmodified. No CDN. No ELK. No SVG `<object>` importer fix.
- `mermaid.initialize({ startOnLoad: false, theme: "neutral" }); mermaid.run();` Keep mermaid default `strict`.
- Tests run in Docker: `cd sandbox && rtk make test ARGS='tests/test_mermaid_verbatim.py -v'`.
- After Python edits: `rtk .venv/bin/ruff`, `rtk .venv/bin/mypy`, `rtk make napoleon-gate`. Then `graphify update .`.
- No new Python package (mermaid is JS).

## File structure

- Create: `sphinx_hosting/mermaid.py` — `wrap_mermaid_verbatim`
- Create: `sandbox/tests/test_mermaid_verbatim.py`
- Create: `sphinx_hosting/static/sphinx_hosting/js/mermaid.min.js` (upstream 11.12.1 UMD)
- Modify: `sphinx_hosting/wildewidgets/sphinx_page.py` — `SphinxPageBodyWidget`
- Modify: `sphinx_hosting/templates/sphinx_hosting/base.html` — script after MathJax
- Modify: `sphinx_hosting/static/sphinx_hosting/css/sphinx_hosting.css` — overflow rule

---

### Task 1: `wrap_mermaid_verbatim`

**Files:**
- Create: `sphinx_hosting/mermaid.py`
- Test: `sandbox/tests/test_mermaid_verbatim.py`

**Interfaces:**
- Consumes: Page Body `str` (HTML + optional Django tags)
- Produces: `wrap_mermaid_verbatim(body: str) -> str`

- [ ] **Step 1: Write the failing tests**

```python
# ruff: noqa: S101

from __future__ import annotations

from django.template import Context, Template

from sphinx_hosting.mermaid import wrap_mermaid_verbatim


def test_wraps_pre_mermaid_and_template_keeps_mustaches() -> None:
    body = '<p>before</p><pre class="mermaid">graph TD; A-->B; {{node}}</pre><p>after</p>'
    wrapped = wrap_mermaid_verbatim(body)
    assert wrapped.startswith("<p>before</p>{% verbatim %}")
    assert wrapped.endswith("{% endverbatim %}<p>after</p>")
    html = Template("{% load sphinx_hosting %}\n" + wrapped).render(Context())
    assert "{{node}}" in html
    assert "graph TD" in html


def test_wraps_div_and_extra_classes() -> None:
    body = '<div class="mermaid align-center">sequenceDiagram\nA->>B: hi</div>'
    wrapped = wrap_mermaid_verbatim(body)
    assert wrapped.startswith("{% verbatim %}<div class=\"mermaid align-center\">")
    assert wrapped.endswith("</div>{% endverbatim %}")


def test_skips_highlight_mermaid_and_language_mermaid() -> None:
    pygments = (
        '<div class="highlight-mermaid"><pre>graph TD; A-->B; {{x}}</pre></div>'
        '<code class="language-mermaid">graph TD</code>'
    )
    assert wrap_mermaid_verbatim(pygments) == pygments


def test_leaves_image_tags_outside_mermaid() -> None:
    body = (
        '{% sphinx_image "foo.png" %}'
        '<pre class="mermaid">graph TD; A-->B</pre>'
    )
    wrapped = wrap_mermaid_verbatim(body)
    assert wrapped.startswith('{% sphinx_image "foo.png" %}')


def test_empty_and_plain_html_unchanged() -> None:
    assert wrap_mermaid_verbatim("") == ""
    assert wrap_mermaid_verbatim("<p>no diagram</p>") == "<p>no diagram</p>"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd sandbox && rtk make test ARGS='tests/test_mermaid_verbatim.py -v'`

Expected: FAIL import `sphinx_hosting.mermaid` (or `wrap_mermaid_verbatim` missing).

- [ ] **Step 3: Write minimal implementation**

```python
"""Render-time helpers for mermaid blocks in a Page Body."""

from __future__ import annotations

import re

#: Matches ``<pre>`` / ``<div>`` tags that may carry a class list.
_HTML_BLOCK = re.compile(
    r"<(pre|div)\b([^>]*\bclass=(['\"])([^'\"]*)\3[^>]*)>(.*?)</\1>",
    flags=re.DOTALL | re.IGNORECASE,
)


def wrap_mermaid_verbatim(body: str) -> str:
    """
    Wrap mermaid elements in ``{% verbatim %}`` so Django ``Template``
    does not interpret ``{{`` / ``{%`` inside diagram source.

    Only elements whose class list contains the token ``mermaid`` are
    wrapped. ``highlight-mermaid`` is not that token.

    Args:
        body: Page Body HTML, possibly mixed with Django template tags.

    Returns:
        ``body`` with mermaid blocks wrapped, or ``body`` unchanged.

    """
    if not body:
        return body

    def _replace(match: re.Match[str]) -> str:
        classes = match.group(4).split()
        if "mermaid" not in classes:
            return match.group(0)
        return "{% verbatim %}" + match.group(0) + "{% endverbatim %}"

    return _HTML_BLOCK.sub(_replace, body)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd sandbox && rtk make test ARGS='tests/test_mermaid_verbatim.py -v'`

Expected: PASS (5 tests). `test_leaves_image_tags_outside_mermaid` only checks the tag is not eaten by wrap; it does not render `{% sphinx_image %}` (that tag needs a real image context).

- [ ] **Step 5: Quality gate on the new Python file**

Run:

```bash
rtk .venv/bin/ruff check sphinx_hosting/mermaid.py sandbox/tests/test_mermaid_verbatim.py
rtk .venv/bin/mypy sphinx_hosting/mermaid.py
rtk make napoleon-gate
```

Expected: no new issues.

- [ ] **Step 6: Commit**

```bash
git add sphinx_hosting/mermaid.py sandbox/tests/test_mermaid_verbatim.py
git commit -m "$(cat <<'EOF'
feat: wrap mermaid Page Body blocks in verbatim at render

EOF
)"
```

---

### Task 2: Wire `SphinxPageBodyWidget`

**Files:**
- Modify: `sphinx_hosting/wildewidgets/sphinx_page.py` (`SphinxPageBodyWidget.__init__`)
- Test: `sandbox/tests/test_mermaid_verbatim.py`

**Interfaces:**
- Consumes: `wrap_mermaid_verbatim(body: str) -> str`
- Produces: widget still takes `page: SphinxPage`; `page.body` is wrapped before `Template()`

- [ ] **Step 1: Add a widget test that fails until wrap is wired**

Append to `sandbox/tests/test_mermaid_verbatim.py`:

```python
from types import SimpleNamespace

from sphinx_hosting.wildewidgets.sphinx_page import SphinxPageBodyWidget


def test_body_widget_preserves_mustaches_in_mermaid() -> None:
    page = SimpleNamespace(
        body='<pre class="mermaid">graph TD; A-->{{node}}</pre>'
    )
    widget = SphinxPageBodyWidget(page)
    html = widget.widget.html  # wildewidgets HTMLWidget stores html= on self.html
    assert "{{node}}" in html
    assert "graph TD" in html
```

Do not parse the Page Body with lxml.

- [ ] **Step 2: Run the new test**

Run: `cd sandbox && rtk make test ARGS='tests/test_mermaid_verbatim.py::test_body_widget_preserves_mustaches_in_mermaid -v'`

Expected: FAIL (`{{node}}` missing) because `SphinxPageBodyWidget` still templates raw `page.body`.

- [ ] **Step 3: Wire wrap before `Template()`**

In `sphinx_hosting/wildewidgets/sphinx_page.py`, add:

```python
from ..mermaid import wrap_mermaid_verbatim
```

Change `SphinxPageBodyWidget.__init__` to:

```python
    def __init__(self, page: SphinxPage, **kwargs):
        super().__init__(**kwargs)
        body = "{% load sphinx_hosting %}\n" + wrap_mermaid_verbatim(page.body)
        self.widget = HTMLWidget(html=Template(body).render(Context()))
```

Do not change stored `page.body`. Do not wrap at import.

- [ ] **Step 4: Run the mermaid test module**

Run: `cd sandbox && rtk make test ARGS='tests/test_mermaid_verbatim.py -v'`

Expected: PASS all tests in that file.

- [ ] **Step 5: Quality gate**

```bash
rtk .venv/bin/ruff check sphinx_hosting/wildewidgets/sphinx_page.py sphinx_hosting/mermaid.py sandbox/tests/test_mermaid_verbatim.py
rtk .venv/bin/mypy sphinx_hosting/wildewidgets/sphinx_page.py sphinx_hosting/mermaid.py
rtk make napoleon-gate
```

- [ ] **Step 6: Commit**

```bash
git add sphinx_hosting/wildewidgets/sphinx_page.py sandbox/tests/test_mermaid_verbatim.py
git commit -m "$(cat <<'EOF'
feat: verbatim-wrap mermaid in SphinxPageBodyWidget

EOF
)"
```

---

### Task 3: Vendor mermaid, load it, overflow CSS

**Files:**
- Create: `sphinx_hosting/static/sphinx_hosting/js/mermaid.min.js`
- Modify: `sphinx_hosting/templates/sphinx_hosting/base.html`
- Modify: `sphinx_hosting/static/sphinx_hosting/css/sphinx_hosting.css` (add rule next to existing `.sphinxpage-body` rules, after line 409)
- Test: `sandbox/tests/test_mermaid_verbatim.py`

**Interfaces:**
- Consumes: none from Task 1 besides the already-rendered `.mermaid` HTML
- Produces: static URL `sphinx_hosting/js/mermaid.min.js`; footer init as specified in Global Constraints

- [ ] **Step 1: Write failing presence tests**

Append to `sandbox/tests/test_mermaid_verbatim.py`:

```python
from pathlib import Path

import sphinx_hosting

# Tests run in the demo container. The app is mounted as the installed
# package, not as a git-root relative to this test file.
_APP = Path(sphinx_hosting.__file__).resolve().parent


def test_vendored_mermaid_is_1121_umd() -> None:
    path = _APP / "static/sphinx_hosting/js/mermaid.min.js"
    text = path.read_text(encoding="utf-8")
    assert path.stat().st_size > 100_000
    assert "11.12.1" in text


def test_base_template_loads_vendored_mermaid_and_runs() -> None:
    html = (_APP / "templates/sphinx_hosting/base.html").read_text(encoding="utf-8")
    assert "sphinx_hosting/js/mermaid.min.js" in html
    assert "cdn.jsdelivr" not in html
    assert "cdnjs.cloudflare.com/ajax/libs/mermaid" not in html
    assert "startOnLoad: false" in html
    assert 'theme: "neutral"' in html
    assert "mermaid.run()" in html


def test_css_scrolls_wide_mermaid() -> None:
    css = (_APP / "static/sphinx_hosting/css/sphinx_hosting.css").read_text(
        encoding="utf-8"
    )
    assert ".sphinxpage-body .mermaid" in css
    assert "overflow-x: auto" in css
```

- [ ] **Step 2: Run those tests**

Run: `cd sandbox && rtk make test ARGS='tests/test_mermaid_verbatim.py::test_vendored_mermaid_is_1121_umd tests/test_mermaid_verbatim.py::test_base_template_loads_vendored_mermaid_and_runs tests/test_mermaid_verbatim.py::test_css_scrolls_wide_mermaid -v'`

Expected: FAIL (`mermaid.min.js` missing and/or strings absent).

- [ ] **Step 3: Vendor mermaid 11.12.1 UMD**

```bash
mkdir -p sphinx_hosting/static/sphinx_hosting/js
curl -fsSL -o sphinx_hosting/static/sphinx_hosting/js/mermaid.min.js \
  https://cdn.jsdelivr.net/npm/mermaid@11.12.1/dist/mermaid.min.js
```

Do not edit the downloaded file. Do not add ELK. Do not add a `.map`. Confirm `11.12.1` appears in the file (mermaid stamps the version). If it does not, stop and pick the official npm tarball `package/dist/mermaid.min.js` for `mermaid@11.12.1` instead of guessing another CDN path.

- [ ] **Step 4: Load and initialize in `base.html`**

Replace the `extra_footer_js` block with:

```html
{% block extra_footer_js %}
{{ block.super }}
<script src="https://cdnjs.cloudflare.com/ajax/libs/fslightbox/3.4.1/index.js" integrity="sha512-jrYR1cG7wwq2l+uNH+XXF18hjN+j8MBjM2PK2+fV/nAIHKxqpg479rOWFOxTpCnyPMZeGAi+eDAxHyrzTzkyRg==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
<script async="async" src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-mml-chtml.min.js" integrity="sha512-6FaAxxHuKuzaGHWnV00ftWqP3luSBRSopnNAA2RvQH1fOfnF/A1wOfiUWF7cLIOFcfb1dEhXwo5VG3DAisocRw==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
<script src="{% static 'sphinx_hosting/js/mermaid.min.js' %}"></script>
<script>
    fsLightbox.props.type = "image";
    mermaid.initialize({ startOnLoad: false, theme: "neutral" });
    mermaid.run();
</script>
{% endblock %}
```

Keep MathJax and fslightbox as they are. Do not add a mermaid settings key.

- [ ] **Step 5: Add overflow CSS**

Insert immediately after the `/* -- main layout ----------------------------------------------------------- */` comment (before `.sphinxpage-body .wildewidgets_html_container`):

```css
.sphinxpage-body .mermaid {
  overflow-x: auto;
}
```

- [ ] **Step 6: Re-run presence tests**

Run: `cd sandbox && rtk make test ARGS='tests/test_mermaid_verbatim.py -v'`

Expected: PASS entire module.

- [ ] **Step 7: Commit**

```bash
git add \
  sphinx_hosting/static/sphinx_hosting/js/mermaid.min.js \
  sphinx_hosting/templates/sphinx_hosting/base.html \
  sphinx_hosting/static/sphinx_hosting/css/sphinx_hosting.css \
  sandbox/tests/test_mermaid_verbatim.py
git commit -m "$(cat <<'EOF'
feat: vendor mermaid 11.12.1 and init on docs pages

EOF
)"
```

- [ ] **Step 8: Graphify**

Run: `graphify update .`

Expected: incremental AST update succeeds.

---

## Out of scope (do not do)

- Import-time HTML rewrite
- `language-mermaid` / Pygments fences as diagrams
- ELK layout package
- Rewriting Sphinx SVG `<object data>` in the importer
- Dark-theme hook, zoom, per-page script detect, `SPHINX_HOSTING_SETTINGS`

## Self-review

- ADR host-side + vendor + verbatim-at-render + `.mermaid` only + overflow + `run()` + no setting: Tasks 1–3.
- SVG `<object>` / ELK / fences: listed out of scope, matching ADR.
- No TBD placeholders. `wrap_mermaid_verbatim` name is consistent across tasks.
