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
