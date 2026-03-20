from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, Any, Protocol, cast

from django.conf import settings as django_settings
from django.utils.module_loading import import_string

from .settings import PROJECT_DETAIL_LAYOUT_BUILDERS_SETTING

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser
    from django.http import HttpRequest
    from wildewidgets import WidgetListLayout

    from .models import Project

    class ProjectDetailLayoutView(Protocol):
        """
        Protocol for views that host project-detail layout builders.

        Both the read-only project detail view and the editable project update
        view satisfy this protocol.
        """

        request: HttpRequest

#: The setting path used in validation error messages for project-detail builders.
PROJECT_DETAIL_LAYOUT_BUILDERS_SOURCE: str = (
    "SPHINX_HOSTING_SETTINGS['PROJECT_DETAIL_LAYOUT_BUILDERS']"
)


class ProjectDetailLayoutBuilder(Protocol):
    """
    Protocol for a project-detail layout builder callable.

    The callable receives the live
    :py:class:`wildewidgets.WidgetListLayout` instance for a
    :py:class:`sphinx_hosting.views.ProjectDetailView` request and may mutate it
    in place.
    """

    def __call__(
        self,
        *,
        request: HttpRequest,
        user: AbstractUser,
        project: Project,
        layout: WidgetListLayout,
        view: ProjectDetailLayoutView,
    ) -> None:
        """
        Customize a project-detail page layout.

        Keyword Args:
            request: The current Django request.
            user: The authenticated user for the request.
            project: The project being displayed.
            layout: The live ``WidgetListLayout`` instance to mutate.
            view: The active project detail or update view instance.

        Side Effects:
            Mutates ``layout`` in place.

        """


@lru_cache(maxsize=64)
def _resolve_project_detail_layout_builders(
    paths: tuple[str, ...],
) -> tuple[ProjectDetailLayoutBuilder, ...]:
    """
    Resolve dotted import paths to project-detail layout builders.

    Args:
        paths: Dotted import paths for layout builder callables.

    Returns:
        A tuple of resolved project-detail layout builder callables.

    Raises:
        TypeError: One or more resolved objects is not callable.

    """
    builders: list[ProjectDetailLayoutBuilder] = []
    for path in paths:
        builder = import_string(path)
        if not callable(builder):
            msg = (
                f"{PROJECT_DETAIL_LAYOUT_BUILDERS_SOURCE} path '{path}' resolved to "
                f"'{type(builder).__name__}', which is not callable."
            )
            raise TypeError(msg)
        builders.append(cast("ProjectDetailLayoutBuilder", builder))
    return tuple(builders)


def get_project_detail_layout_builders() -> tuple[ProjectDetailLayoutBuilder, ...]:
    """
    Return configured project-detail layout builders.

    Returns:
        A tuple of resolved project-detail layout builder callables.

    Raises:
        TypeError: ``PROJECT_DETAIL_LAYOUT_BUILDERS`` is not a list of
            dotted-path strings.

    """
    app_settings: dict[str, Any] = getattr(
        django_settings, "SPHINX_HOSTING_SETTINGS", {}
    )
    raw_paths = app_settings.get(PROJECT_DETAIL_LAYOUT_BUILDERS_SETTING, [])
    if raw_paths is None:
        return ()
    if not isinstance(raw_paths, list):
        msg = (
            f"{PROJECT_DETAIL_LAYOUT_BUILDERS_SOURCE} must be a list of "
            "dotted-path strings."
        )
        raise TypeError(msg)
    for index, path in enumerate(raw_paths):
        if not isinstance(path, str):
            msg = (
                f"{PROJECT_DETAIL_LAYOUT_BUILDERS_SOURCE}[{index}] must be a "
                f"dotted-path string, got '{type(path).__name__}'."
            )
            raise TypeError(msg)
    return _resolve_project_detail_layout_builders(tuple(raw_paths))


def apply_project_detail_layout_builders(
    *,
    request: HttpRequest,
    user: AbstractUser,
    project: Project,
    layout: WidgetListLayout,
    view: ProjectDetailLayoutView,
) -> None:
    """
    Apply configured project-detail layout builders to ``layout``.

    Keyword Args:
        request: The current Django request.
        user: The authenticated user for the request.
        project: The project being displayed.
        layout: The live ``WidgetListLayout`` instance to mutate.
        view: The active project detail or update view instance.

    Side Effects:
        Allows configured builder callables to mutate ``layout`` in place.

    """
    for builder in get_project_detail_layout_builders():
        builder(
            request=request,
            user=user,
            project=project,
            layout=layout,
            view=view,
        )
