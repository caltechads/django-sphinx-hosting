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
    title: str = "Main"
    items = [
        MenuItem(
            text='Projects',
            icon='bookshelf',
            url=reverse_lazy('sphinx_hosting:project--list')
        )
    ]


class SphinxHostingLookupsMenu(Menu):
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

    items: List[BreadcrumbItem] = [
        BreadcrumbItem(
            title='Sphinx Hosting',
            url=reverse_lazy('sphinx_hosting:project--list')
        )
    ]
