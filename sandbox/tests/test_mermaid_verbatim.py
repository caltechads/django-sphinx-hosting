# ruff: noqa: S101

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
