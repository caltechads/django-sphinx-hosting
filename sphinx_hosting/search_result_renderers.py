from __future__ import annotations

from functools import lru_cache
from importlib import import_module
from typing import TYPE_CHECKING, Any, Protocol, cast

from django.apps import apps
from django.conf import settings as django_settings
from django.utils.module_loading import import_string
from haystack import connections
from haystack.exceptions import NotHandled

from .models import SphinxPage
from .settings import SEARCH_RESULT_RENDERERS_SETTING

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser
    from django.db.models import Model
    from django.http import HttpRequest
    from haystack.models import SearchResult
    from wildewidgets import Widget

    from .views import GlobalSphinxPageSearchView

#: The setting path used in validation error messages for search result renderers.
SEARCH_RESULT_RENDERERS_SOURCE: str = (
    "SPHINX_HOSTING_SETTINGS['SEARCH_RESULT_RENDERERS']"
)


class SearchResultRenderer(Protocol):
    """
    Protocol for a unified-search result renderer callable.

    Each renderer converts one Haystack ``SearchResult`` for a registered host
    model into one ready-to-render ``wildewidgets.Widget``.
    """

    def __call__(
        self,
        *,
        result: SearchResult,
        request: HttpRequest,
        user: AbstractUser,
        view: GlobalSphinxPageSearchView,
    ) -> Widget:
        """
        Render a unified-search hit.

        Keyword Args:
            result: The Haystack search hit to render.
            request: The current Django request.
            user: The authenticated user for this request.
            view: The active global-search view instance.

        Returns:
            The widget used to render the search hit.

        """


@lru_cache(maxsize=64)
def _resolve_search_result_renderers(
    entries: tuple[tuple[str, str], ...],
) -> tuple[tuple[type[Model], SearchResultRenderer], ...]:
    """
    Resolve configured model labels and renderer paths.

    Args:
        entries: Tuples of Django model label and renderer dotted path.

    Returns:
        A tuple of resolved model/renderer pairs.

    Raises:
        LookupError: One or more model labels does not resolve to an installed
            model or lacks a registered Haystack index.
        TypeError: One or more resolved renderer objects is not callable.

    """
    unified_index = connections["default"].get_unified_index()
    renderers: list[tuple[type[Model], SearchResultRenderer]] = []
    for model_label, path in entries:
        try:
            model = apps.get_model(model_label)
        except LookupError as exc:
            msg = (
                f"{SEARCH_RESULT_RENDERERS_SOURCE} key '{model_label}' does not "
                "resolve to a Django model."
            )
            raise LookupError(msg) from exc
        try:
            unified_index.get_index(model)
        except NotHandled as exc:
            msg = (
                f"{SEARCH_RESULT_RENDERERS_SOURCE} key '{model_label}' must refer "
                "to a model with a registered Haystack SearchIndex."
            )
            raise LookupError(msg) from exc
        renderer = import_string(path)
        if not callable(renderer):
            msg = (
                f"{SEARCH_RESULT_RENDERERS_SOURCE} path '{path}' resolved to "
                f"'{type(renderer).__name__}', which is not callable."
            )
            raise TypeError(msg)
        renderers.append((model, cast("SearchResultRenderer", renderer)))
    return tuple(renderers)


def get_search_result_renderers() -> dict[type[Model], SearchResultRenderer]:
    """
    Return configured host-model search result renderers.

    Returns:
        A mapping of Django model class to search result renderer callable.

    Raises:
        TypeError: ``SEARCH_RESULT_RENDERERS`` is not a dict whose keys are
            string model labels and whose values are dotted-path strings.
        LookupError: One or more configured model labels is invalid or lacks a
            registered Haystack index.

    """
    app_settings: dict[str, Any] = getattr(
        django_settings, "SPHINX_HOSTING_SETTINGS", {}
    )
    raw_renderers = app_settings.get(SEARCH_RESULT_RENDERERS_SETTING, {})
    if raw_renderers is None:
        return {}
    if not isinstance(raw_renderers, dict):
        msg = f"{SEARCH_RESULT_RENDERERS_SOURCE} must be a dict."
        raise TypeError(msg)
    for model_label, path in raw_renderers.items():
        if not isinstance(model_label, str):
            msg = (
                f"{SEARCH_RESULT_RENDERERS_SOURCE} keys must be Django model "
                f"labels as strings, got '{type(model_label).__name__}'."
            )
            raise TypeError(msg)
        if not isinstance(path, str):
            msg = (
                f"{SEARCH_RESULT_RENDERERS_SOURCE}['{model_label}'] must be a "
                f"dotted-path string, got '{type(path).__name__}'."
            )
            raise TypeError(msg)
    return dict(_resolve_search_result_renderers(tuple(raw_renderers.items())))


def get_search_result_models() -> tuple[type[Model], ...]:
    """
    Return host-model classes included in unified global search.

    Returns:
        A tuple of registered host-model classes in settings order.

    """
    return tuple(get_search_result_renderers())


def build_search_result_widget(
    *,
    result: SearchResult,
    request: HttpRequest,
    user: AbstractUser,
    view: GlobalSphinxPageSearchView,
) -> Widget:
    """
    Build the widget used to render one unified-search result.

    Keyword Args:
        result: The Haystack search hit to render.
        request: The current Django request.
        user: The authenticated user for this request.
        view: The active global-search view instance.

    Returns:
        The widget used to render the search hit.

    Raises:
        LookupError: No renderer is configured for a non-``SphinxPage`` hit.

    """
    if result.model is SphinxPage:
        search_module = import_module("sphinx_hosting.wildewidgets.search")

        return search_module.SearchResultBlock(object=result)

    renderers = get_search_result_renderers()
    try:
        renderer = renderers[result.model]
    except KeyError as exc:
        msg = (
            f"No unified-search renderer is configured for model "
            f"'{result.app_label}.{result.model_name}'."
        )
        raise LookupError(msg) from exc
    return renderer(result=result, request=request, user=user, view=view)
