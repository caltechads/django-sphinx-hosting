from typing import List, Tuple

from django.templatetags.static import static
from django.urls import reverse, reverse_lazy
from wildewidgets import BreadrumbBlock, VerticalDarkMenu

from .core import (
    LinkedImage,
    Menu,
    MenuItem,
    TablerVerticalNavbar
)


class SphinxHostingMenu(VerticalDarkMenu):
    """
    A main menu for all ``sphinx_hosting`` views.   To use it, subclass this and:

    * Add your own menu items it :py:attr:`items`
    * Change the menu logo by updating :py:attr:`brand_image`
    * Change the menu logo alt text by updating :py:attr:`brand_text`
    """

    brand_image: str = static("sphinx_hosting/images/logo.jpg")
    brand_image_width: str = '100%'
    brand_text: str = "Sphinx Hosting"
    items: List[Tuple[str, str]] = [
        ('Projects', 'sphinx_hosting:project--list'),
    ]


class SphinxHostingMainMenu(Menu):
    items = [
        MenuItem(
            text='Administration',
            icon='bullseye',
            items=[
                MenuItem(
                    text='Projects',
                    icon='bookshelf',
                    url=reverse_lazy('sphinx_hosting:project--list')
                )
            ]
        )
    ]


class SphinxHostingSidebar(TablerVerticalNavbar):

    branding = LinkedImage(
        image_src=static("sphinx_hosting/images/logo.jpg"),
        image_width='100%',
        image_alt="Sphinx Hosting",
        url="/"
    )
    contents = [
        SphinxHostingMainMenu()
    ]


class SphinxHostingBreadcrumbs(BreadrumbBlock):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_breadcrumb('Sphinx Hosting', reverse('sphinx_hosting:project--list'))
