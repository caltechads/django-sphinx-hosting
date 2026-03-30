from __future__ import annotations

from typing import TYPE_CHECKING, cast

import humanize
from django.utils import timezone
from wildewidgets import Block, HorizontalLayoutBlock, LinkButton

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser
    from django.http import HttpRequest
    from haystack.models import SearchResult
    from wildewidgets import Widget

    from sphinx_hosting.views import GlobalSphinxPageSearchView

    from .models import SearchNote


class SearchNoteResultBlock(Block):
    """
    Result card used to render a demo ``SearchNote`` search hit.

    Args:
        note: The note represented by this search result.
        score: The backend-provided relevance score for the note.

    """

    def __init__(self, note: SearchNote, score: float, **kwargs):
        """
        Initialize this demo search-result card.

        Args:
            note: The note represented by this search result.
            score: The backend-provided relevance score for the note.

        Keyword Args:
            **kwargs: Keyword arguments forwarded to ``Block``.

        """
        super().__init__(**kwargs)
        self.add_class("shadow")
        self.add_class("border")
        self.add_class("p-4")
        self.add_class("mb-4")
        age = humanize.naturaldelta(
            timezone.now() - note.modified, minimum_unit="seconds"
        )
        self.add_block(
            HorizontalLayoutBlock(
                Block(
                    "Demo Search Note",
                    css_class="fs-6 text-muted font-bold",
                ),
                Block(
                    f"{age} ago",
                    css_class="text-muted fs-6 text-uppercase",
                ),
                justify="between",
                align="baseline",
                css_class="mb-3",
            )
        )
        self.add_block(Block(note.title, tag="h3"))
        self.add_block(
            Block(
                note.body[:200].rsplit(" ", 1)[0] + "...",
                css_class="fs-8 text-muted mb-3",
            )
        )
        self.add_block(
            HorizontalLayoutBlock(
                LinkButton(text="Open Note", url=note.get_absolute_url()),
                Block(f"Rank: {score}", css_class="fs-6 text-muted"),
                justify="between",
                align="baseline",
            )
        )


def render_search_note_result(
    *,
    result: SearchResult,
    request: HttpRequest,
    user: AbstractUser,
    view: GlobalSphinxPageSearchView,
) -> Widget:
    """
    Render one demo ``SearchNote`` unified-search result.

    Keyword Args:
        result: The Haystack search hit to render.
        request: The current Django request.
        user: The authenticated user for this request.
        view: The active global-search view.

    Returns:
        The widget used to render the note search hit.

    """
    del request, user, view
    note = cast("SearchNote", result.object)
    return SearchNoteResultBlock(note=note, score=result.score)
