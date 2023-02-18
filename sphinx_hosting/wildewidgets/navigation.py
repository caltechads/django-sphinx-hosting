from typing import List
from django.templatetags.static import static
from django.urls import reverse_lazy
from wildewidgets import (
    BreadcrumbBlock,
    BreadcrumbItem,
    LinkedImage,
    Menu,
    MenuItem,
    TablerVerticalNavbar
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
            icon='bookshelf',
            url=reverse_lazy('sphinx_hosting:project--list')
        )
    ]


class SphinxHostingLookupsMenu(Menu):
    """
    This is a second menu that appears in :py:class:`SphinxHostingSidebar` below
    the main menu, :py:class:`SphinxHostingMainMenu`.  This gives access to our
    various lookup models like :py:class:`sphinx_hosting.models.Classifier` for
    those users that have rights to work with them directly.
    """
    title: str = "Lookups"
    css_class: str = 'mt-3'
    items = [
        MenuItem(
            text='Classifiers',
            icon='bookshelf',
            url=reverse_lazy('sphinx_hosting:classifier--index')
        )
    ]


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

    wide = True
    branding = LinkedImage(
        image_src=static("sphinx_hosting/images/logo.jpg"),
        image_width='100%',
        image_alt="Sphinx Hosting",
        url="/"
    )
    contents = [
        GlobalSearchFormWidget(),
        SphinxHostingMainMenu(),
        SphinxHostingLookupsMenu(),
    ]


class SphinxHostingBreadcrumbs(BreadcrumbBlock):
    """
    """

    items: List[BreadcrumbItem] = [
        BreadcrumbItem(
            title='Sphinx Hosting',
            url=reverse_lazy('sphinx_hosting:project--list')
        )
    ]
