# ruff: noqa: S101, PLR2004

from __future__ import annotations

from django.template import Context, Template

from sphinx_hosting.mermaid import wrap_mermaid_verbatim


def test_wraps_pre_mermaid_and_template_keeps_mustaches() -> None:
    body = (
        '<p>before</p><pre class="mermaid">graph TD; A-->B; {{node}}</pre>'
        "<p>after</p>"
    )
    wrapped = wrap_mermaid_verbatim(body)
    assert wrapped.startswith("<p>before</p>{% verbatim %}")
    assert wrapped.endswith("{% endverbatim %}<p>after</p>")
    html = Template("{% load sphinx_hosting %}\n" + wrapped).render(Context())
    assert "{{node}}" in html
    assert "graph TD" in html


def test_wraps_div_and_extra_classes() -> None:
    body = '<div class="mermaid align-center">sequenceDiagram\nA->>B: hi</div>'
    wrapped = wrap_mermaid_verbatim(body)
    assert wrapped.startswith('{% verbatim %}<div class="mermaid align-center">')
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
