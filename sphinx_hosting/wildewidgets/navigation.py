from django.templatetags.static import static
from django.urls import reverse, reverse_lazy
from wildewidgets import (
    BreadrumbBlock,
    LinkedImage,
    Menu,
    MenuItem,
    TablerVerticalNavbar
)


class SphinxHostingMainMenu(Menu):
    title: str = "Main"
    items = [
        MenuItem(
            text='Projects',
            icon='bookshelf',
            url=reverse_lazy('sphinx_hosting:project--list')
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
        SphinxHostingMainMenu()
    ]


class SphinxHostingBreadcrumbs(BreadrumbBlock):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_breadcrumb('Sphinx Hosting', reverse('sphinx_hosting:project--list'))
