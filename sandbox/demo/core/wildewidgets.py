from __future__ import annotations

from typing import TYPE_CHECKING, Any

from wildewidgets import Block, CardWidget

from sphinx_hosting.wildewidgets import SphinxHostingSidebar

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser
    from django.http.request import HttpRequest
    from wildewidgets import WidgetListLayout

    from sphinx_hosting.models import Project
    from sphinx_hosting.views import ProjectDetailView
    from sphinx_hosting.wildewidgets import SphinxHostingMainMenu

# ------------------------------------------------------
# Menus
# ------------------------------------------------------


def build_support_menu_item(
    *, request: HttpRequest, user: AbstractUser, menu: SphinxHostingMainMenu
) -> dict[str, Any]:
    """
    Return a demo support link for conditional menu-builder integration tests.

    Keyword Args:
        request: The current Django request.
        user: The authenticated user for this request.
        menu: The ``SphinxHostingMainMenu`` instance being built.

    Returns:
        A dictionary menu item specification.

    """
    del request, user, menu
    return {"text": "Support", "icon": "life-preserver", "url": "/support/"}


def extend_project_detail_layout(
    *,
    request: HttpRequest,
    user: AbstractUser,
    project: Project,
    layout: WidgetListLayout,
    view: ProjectDetailView,
) -> None:
    """
    Add demo host-project content to the project detail layout.

    Keyword Args:
        request: The current Django request.
        user: The authenticated user for this request.
        project: The project being displayed.
        layout: The live ``WidgetListLayout`` instance to mutate.
        view: The active ``ProjectDetailView`` instance.

    Side Effects:
        Appends a host-project widget and sidebar action to ``layout``.

    """
    del request, user, view
    widget = CardWidget(
        widget=Block("Demo host projects can append ecosystem-specific content here."),
    )
    widget.icon = "boxes"
    widget.title = "Host Ecosystem"
    layout.add_widget(widget)
    layout.add_sidebar_link_button(
        "Project Support",
        f"/support/projects/{project.machine_name}/",
        color="teal",
    )


class MainMenu(SphinxHostingSidebar):
    """
    Demo override class for ``SPHINX_HOSTING_SETTINGS['NAVBAR_CLASS']`` tests.
    """
