from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sphinx_hosting.wildewidgets import SphinxHostingSidebar

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser
    from django.http.request import HttpRequest

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


class MainMenu(SphinxHostingSidebar):
    """
    Demo override class for ``SPHINX_HOSTING_SETTINGS['NAVBAR_CLASS']`` tests.
    """
