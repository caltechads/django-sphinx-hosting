from typing import List, Optional, cast

from crequest.middleware import CrequestMiddleware
from django.contrib.auth.models import AbstractUser
from django.http.request import HttpRequest
from django.urls import reverse_lazy
from wildewidgets import (
    Block,
    BreadcrumbBlock,
    BreadcrumbItem,
    LinkedImage,
    Menu,
    MenuItem,
    TablerVerticalNavbar
)

from ..settings import (
    LOGO_IMAGE,
    LOGO_URL,
    LOGO_WIDTH,
    SITE_NAME
)
from .search import GlobalSearchFormWidget


class SphinxHostingMainMenu(Menu):
    """
    This is the primary menu that appears in :py:class:`SphinxHostingSidebar`
    directly underneath the "Search" form,
    :py:class:`sphinx_hosting.wildewidgets.search.GlobalSearchFormWidget`.

    It gives access to all the views that normal, non privileged users should be
    allowed to use.
    """
    title: str = "Main"
    items = [
        MenuItem(
            text='Projects',
            icon='stack',
            url=reverse_lazy('sphinx_hosting:project--list')
        )
    ]

    def __init__(self, *items, **kwargs) -> None:
        self.active_item: Optional[str] = None
        super().__init__(*items, **kwargs)

    def build_menu(self, items: List[MenuItem]) -> None:
        """
        Programatically build our menu here.  We have this code because the
        presence of some items in this menu depends on the user's permissions.

        We have to do it here because if we do it in ``__init__``, that's too
        early in the Django boostrap and the global Django ``urlpatterns`` have
        not finished building, and even ``reverse_lazy`` fails.
        """
        request: HttpRequest = CrequestMiddleware.get_request()
        user: AbstractUser = cast(AbstractUser, request.user)
        if user.has_perm('sphinxhostingcore.view_classifier'):
            item = MenuItem(
                text='Classifiers',
                icon='sliders',
                url=reverse_lazy('sphinx_hosting:classifier--index')
            )
            items.append(item)
        for item in items:
            if self.active_item is not None:
                item.set_active(self.active_item)
        super().build_menu(items)

    def activate(self, text: str) -> bool:
        """
        Normally, how activate works is that it looks through our menu items,
        finds the one whose ``text`` or ``url`` matches ``text``.

        In our case, we're building the menu items in :py:meth:`build_menu`,
        which occurs after :py:meth:`activate` would be called, so we have to
        save the ``text`` here, and use it later in :py:meth:`build_menu`.

        Args:
            text: the text to search for among our :py:attr:`items`

        Returns:
            We always return ``True`` here, since we won't know if we match
            until later.
        """
        self.active_item = text
        return True


class SphinxHostingSidebar(TablerVerticalNavbar):
    """
    This is the vertical menu area on the left of the page.  It houses our
    search form,
    :py:class:`sphinx_hosting.wildewidgets.search.GlobalSearchFormWidget`, our
    main menu :py:class:`SphinxHostingMainMenu`, possibly our utility menu
    :py:class:`SphinxHostingLookupsMenu` and finally the global navigation
    for a :py:class:`sphinx_hosting.models.Version` when we're reading our
    documentation.
    """

    hide_below_viewport: str = 'xl'
    branding = Block(
        LinkedImage(
            image_src=LOGO_IMAGE,
            image_width=LOGO_WIDTH,
            image_alt=SITE_NAME,
            css_class='d-flex justify-content-center',
            url=LOGO_URL
        ),
        GlobalSearchFormWidget(css_class='ms-auto ms-xl-0 align-self-center mt-3'),
        css_class='d-flex flex-row flex-xl-column justify-content-between flex-grow-1 flex-xl-grow-0'
    )
    contents = [
        SphinxHostingMainMenu(),
    ]
    wide: bool = True


class SphinxHostingBreadcrumbs(BreadcrumbBlock):

    items: List[BreadcrumbItem] = [
        BreadcrumbItem(
            title=SITE_NAME,
            url=reverse_lazy('sphinx_hosting:project--list')
        )
    ]
