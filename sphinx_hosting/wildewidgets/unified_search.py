from __future__ import annotations

from typing import TYPE_CHECKING, cast

from wildewidgets import Block, Column, PagedModelWidget, Row

from ..search_result_renderers import build_search_result_widget
from .search import (
    SearchResultsClassifiersFacet,
    SearchResultsHeader,
    SearchResultsPageHeader,
    SearchResultsProjectFacet,
)

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser
    from django.http import HttpRequest
    from haystack.models import SearchResult
    from haystack.query import SearchQuerySet
    from wildewidgets import Widget

    from ..global_search_view import GlobalSphinxPageSearchView


class UnifiedSearchResultWidget(Block):
    """
    Dispatch one unified-search hit to the correct per-model renderer.

    Keyword Args:
        object: The Haystack ``SearchResult`` to render.
        request: The current Django request.
        view: The active global-search view.

    Raises:
        ValueError: ``request`` or ``view`` was not supplied.

    """

    def __init__(
        self,
        object: SearchResult = None,  # noqa: A002
        *,
        request: HttpRequest | None = None,
        view: GlobalSphinxPageSearchView | None = None,
        **kwargs,
    ):
        """
        Initialize this per-result dispatcher widget.

        Keyword Args:
            object: The Haystack ``SearchResult`` to render.
            request: The current Django request.
            view: The active global-search view.
            **kwargs: Keyword arguments forwarded to ``Block``.

        Raises:
            ValueError: ``request`` or ``view`` was not supplied.

        """
        if request is None:
            msg = "UnifiedSearchResultWidget requires a request."
            raise ValueError(msg)
        if view is None:
            msg = "UnifiedSearchResultWidget requires a view."
            raise ValueError(msg)
        result = cast("SearchResult", object)
        super().__init__(**kwargs)
        self.add_block(
            build_search_result_widget(
                result=result,
                request=request,
                user=cast("AbstractUser", request.user),
                view=view,
            )
        )


class UnifiedPagedSearchResultsBlock(PagedModelWidget):
    """
    Paged listing of mixed-model unified-search result entries.

    Args:
        results: The Haystack search queryset containing our search results.
        query: The text entered into the search form that got us here.

    Keyword Args:
        facets: Active facet values currently applied to the result set.
        view: The active global-search view.
        **kwargs: Keyword arguments forwarded to ``PagedModelWidget``.

    """

    #: The GET parameter used for pagination.
    page_kwarg: str = "p"
    #: The number of search hits displayed per page.
    paginate_by: int = 10
    #: The widget class used to render each search result.
    model_widget: type[Widget] = UnifiedSearchResultWidget

    def __init__(
        self,
        results: SearchQuerySet,
        query: str | None,
        facets: dict[str, list[str]] | None = None,
        *,
        view: GlobalSphinxPageSearchView,
        **kwargs,
    ):
        """
        Initialize the paged unified-search results block.

        Args:
            results: The Haystack search queryset containing our search results.
            query: The text entered into the search form that got us here.

        Keyword Args:
            facets: Active facet values currently applied to the result set.
            view: The active global-search view.
            **kwargs: Keyword arguments forwarded to ``PagedModelWidget``.

        """
        #: The active global-search view used to render each result.
        self.view = view
        if query is not None:
            kwargs["extra_url"] = {"q": query}
            if facets:
                for key, value in facets.items():
                    kwargs["extra_url"][key] = ",".join(value)
        super().__init__(queryset=results, **kwargs)

    def get_model_widgets(self, instances: list[SearchResult]) -> list[Widget]:
        """
        Create widgets for the current page of search results.

        Args:
            instances: The current page of Haystack ``SearchResult`` objects.

        Returns:
            The widgets used to render the current page of results.

        """
        return [
            self.get_model_widget(
                object=instance,
                request=cast("HttpRequest", self.request),
                view=self.view,
            )
            for instance in instances
        ]


class UnifiedPagedSearchLayout(Block):
    """
    The page layout for unified global search results.

    Args:
        results: The Haystack search queryset containing our search results.

    Keyword Args:
        query: The text entered into the search form that got us here.
        facets: Active facet values currently applied to the result set.
        view: The active global-search view.
        **kwargs: Keyword arguments forwarded to ``Block``.

    """

    #: The BEM block name for this layout.
    name: str = "search-layout"
    #: The modifier applied to this search layout.
    modifier: str = "paged"

    def __init__(
        self,
        results: SearchQuerySet,
        query: str | None = None,
        facets: dict[str, list[str]] | None = None,
        *,
        view: GlobalSphinxPageSearchView,
        **kwargs,
    ):
        """
        Initialize the unified-search results page layout.

        Args:
            results: The Haystack search queryset containing our search results.

        Keyword Args:
            query: The text entered into the search form that got us here.
            facets: Active facet values currently applied to the result set.
            view: The active global-search view.
            **kwargs: Keyword arguments forwarded to ``Block``.

        """
        #: The active search query displayed in the page header.
        self.query = query
        if facets is None:
            facets = {}
        super().__init__(**kwargs)
        self.add_block(SearchResultsPageHeader(query, facets=facets))
        self.add_block(SearchResultsHeader(results))
        row = Row()
        row.add_column(
            Column(
                UnifiedPagedSearchResultsBlock(
                    results,
                    query,
                    facets=facets,
                    view=view,
                ),
                name="middle",
                base_width=8,
            )
        )
        row.add_column(
            Column(
                SearchResultsProjectFacet(results, query, css_class="mb-4"),
                SearchResultsClassifiersFacet(results, query),
                name="right",
                base_width=4,
            )
        )
        self.add_block(row)
