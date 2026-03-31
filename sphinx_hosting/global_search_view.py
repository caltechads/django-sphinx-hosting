from __future__ import annotations

from typing import TYPE_CHECKING

from .models import SphinxPage
from .search_result_renderers import get_search_result_models
from .views import GlobalSphinxPageSearchView as BaseGlobalSphinxPageSearchView
from .wildewidgets.unified_search import UnifiedPagedSearchLayout

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse
    from haystack.forms import ModelSearchForm
    from haystack.query import SearchQuerySet
    from wildewidgets import Widget


def _quote_exact_narrow_value(value: str) -> str:
    """
    Escape one exact-match facet value for Haystack narrowing.

    Args:
        value: The raw facet value from the query string.

    Returns:
        The escaped facet value suitable for a narrow query.

    """
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _apply_global_search_facets(
    queryset: SearchQuerySet, request: HttpRequest
) -> tuple[SearchQuerySet, dict[str, list[str]]]:
    """
    Apply active project/classifier filters to a unified-search queryset.

    Args:
        queryset: The base Haystack search queryset.
        request: The current Django request.

    Returns:
        The filtered queryset and the active facets dictionary.

    """
    facets: dict[str, list[str]] = {}
    if project_id := request.GET.get("project_id", None):
        queryset = queryset.narrow(
            f'project_id_exact:"{_quote_exact_narrow_value(project_id)}"'
        )
        facets["project_id"] = [project_id]
    if classifier_name := request.GET.get("classifiers", None):
        queryset = queryset.narrow(
            f'classifiers_exact:"{_quote_exact_narrow_value(classifier_name)}"'
        )
        facets["classifiers"] = [classifier_name]
    return queryset, facets


class GlobalSphinxPageSearchView(BaseGlobalSphinxPageSearchView):
    """
    Unified global search view that blends built-in and host-model hits.

    This subclass preserves the existing search page flow while constraining
    results to ``SphinxPage`` plus registered host models and rendering them
    through the unified search widget dispatcher.
    """

    #: The active search query string shown in the page header.
    query: str | None = None
    #: The active Haystack search queryset for this request.
    queryset: SearchQuerySet
    #: The currently selected facet filters shown in the page header.
    facets: dict[str, list[str]]

    def form_invalid(self, _: ModelSearchForm) -> HttpResponse:
        """
        Render the search page when the submitted form is invalid.

        Args:
            _: The invalid Haystack search form instance. Unused.

        Returns:
            The rendered search page response.

        Side Effects:
            Stores the constrained base queryset and clears the active facets.

        """
        self.queryset = self.get_queryset().models(
            SphinxPage, *get_search_result_models()
        )
        self.object_list = self.queryset
        self.facets = {}
        self.query = None
        context = self.get_context_data()
        return self.render_to_response(context)

    def form_valid(self, form: ModelSearchForm) -> HttpResponse:
        """
        Render the unified-search page for a valid query submission.

        Args:
            form: The validated Haystack search form.

        Returns:
            The rendered search page response.

        Side Effects:
            Stores the constrained queryset, active facets, and active query
            string for the current request.

        """
        self.queryset = form.search().models(SphinxPage, *get_search_result_models())
        self.queryset, self.facets = _apply_global_search_facets(
            self.queryset, self.request
        )
        self.object_list = self.queryset
        self.query = form.cleaned_data[self.search_field]
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_content(self) -> Widget:
        """
        Build the unified-search page layout.

        Returns:
            The populated unified-search results layout.

        """
        return UnifiedPagedSearchLayout(
            self.object_list,
            self.query,
            facets=getattr(self, "facets", {}),
            view=self,
        )
