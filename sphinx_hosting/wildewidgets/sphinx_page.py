from typing import Any, Dict, List

from wildewidgets import (
    Block,
    CardHeader,
    CardWidget,
    HTMLWidget,
    LinkButton,
)
from .core import (
    Column,
    FontIcon,
    Menu,
    MenuItem,
    Row,
    TwoColumnLayoutWidget
)
from ..models import SphinxPage


#------------------------------------------------------
# SphinxPage related widgets
#------------------------------------------------------

class SphinxPagePagination(Row):
    """
    This widget draws the Previous Page, Parent Page and Next Page buttons that
    are found at the top of each
    :py:class:`sphinx_hosting.views.SphinxPageDetailView`.

    It is built out of a Tabler/Bootstrap ``row``, with each of the buttons in
    an equal sized ``col``.
    """

    name: str = 'sphinx-page-navigation'

    def __init__(self, page: SphinxPage, **kwargs):
        super().__init__(**kwargs)
        self.add_column(Column(name='left', alignment='start', viewport_widths={'md': '4'}))
        self.add_column(Column(name='center', alignment='center', viewport_widths={'md': '4'}))
        self.add_column(Column(name='right', alignment='end', viewport_widths={'md': '4'}))
        if hasattr(page, 'previous_page') and page.previous_page.first():
            self.add_to_left(
                LinkButton(
                    text=Block(FontIcon('box-arrow-in-left'), page.previous_page.first().title),
                    url=page.previous_page.first().get_absolute_url(),
                    name=f'{self.name}__previous',
                    css_class='bg-azure-lt'
                )
            )
        if page.parent:
            self.add_to_center(
                LinkButton(
                    text=Block(FontIcon('box-arrow-in-up'), page.parent.title),
                    url=page.parent.get_absolute_url(),
                    name=f'{self.name}__parent',
                    css_class='bg-azure-lt'
                )
            )
        if page.next_page:
            self.add_to_right(
                LinkButton(
                    text=Block(page.next_page.title, FontIcon('box-arrow-in-right')),
                    url=page.next_page.get_absolute_url(),
                    name=f'{self.name}__next',
                    css_class='bg-azure-lt'
                )
            )


class SphinxPageBodyWidget(CardWidget):

    css_class: str = 'sphinxpage-body'

    def __init__(self, page: SphinxPage, **kwargs):
        super().__init__(**kwargs)
        self.widget = HTMLWidget(html=page.body)


class SphinxPageTableOfContentsWidget(CardWidget):

    css_class: str = 'sphinxpage-toc'

    def __init__(self, page: SphinxPage, **kwargs):
        super().__init__(**kwargs)
        self.widget = HTMLWidget(html=page.local_toc)
        self.set_header(
            CardHeader(
                header_level="h3",
                header_text="Table of Contents",
                css_class=''
            )
        )


class SphinxPageGlobalTableOfContentsWidget(CardWidget):

    name: str = 'sphinxpage-globaltoc'

    def __init__(self, page: SphinxPage, **kwargs):
        super().__init__(**kwargs)
        self.widget = HTMLWidget(html=page.version.global_toc)
        self.set_header(
            CardHeader(
                header_level="h3",
                header_text="Project Table of Contents",
                css_class=''
            )
        )


class SphinxPageGlobalTableOfContentsMenu(Menu):

    css_class: str = 'mt-4'
    title_css_classes: str = 'mt-3'

    @classmethod
    def parse_obj(cls, data: Dict[str, Any]) -> "SphinxPageGlobalTableOfContentsMenu":
        """
        Given a dict like this::

            {
                items: [
                    {'text': 'foo'},
                    {'text': 'bar', 'url': '/foo', 'icon': 'blah'}
                    {'text': 'bar', 'url': '/foo', 'icon': 'blah', items: [{'text': 'blah' ...} ...]}
                    ...
                ]
            }

        Return a fully configured :py:class:`SphinxPageGlobalTableOfContentsMenu` suitable
        for insertion into a :py:class:`sphinx_hosting.wildewidgets.Navbar`.

        Returns:
            A configured  ``SphinxPageGlobalTableOfContentsMenu``.
        """
        menu_items = cls._load_menuitems(data['items'])
        return cls(*menu_items)

    @classmethod
    def _load_menuitems(cls, items: List[Dict[str, Any]]) -> List[MenuItem]:
        """
        Given a list like this::

            [
               {'text': 'foo'},
               {'text': 'bar', 'url': '/foo', 'icon': 'blah'}
               {'text': 'bar', 'url': '/foo', 'icon': 'blah', items: [{'text': 'blah' ...} ...]}
                    ...
           ]

        Return a list of :py:class:`sphinx_hosting.wildewidgets.MenuItem`
        objects loaded from that data.

        Returns:
            A list of :py:class:`sphinx_hosting.wildewidgets.MenuItem` objects.
        """
        menu_items: List[MenuItem] = []
        for item in items:
            if 'items' in item:
                sub_items = cls._load_menuitems(item['items'])
                menu_items.append(MenuItem(
                    text=item['text'],
                    url=item.get('url', None),
                    icon=item.get('icon', None),
                    items=sub_items
                ))
            else:
                menu_items.append(MenuItem(**item))
        return menu_items


class SphinxPageTitle(Block):

    block: str = 'sphinxpage-title'
    css_class: str = 'mb-5'

    def __init__(self, page: SphinxPage, **kwargs):
        super().__init__(**kwargs)
        self.project_title = page.version.project.title
        self.version_number = page.version.version
        self.title = page.title
        self.add_block(
            Block(
                f'{self.project_title}-{self.version_number}',
                name='project-title',
                css_class='text-muted fs-6 text-uppercase')
        )
        self.add_block(
            Block(
                self.title,
                tag='h1',
            )
        )


class SphinxPageLayout(Block):
    """
    The page layout for a single :py:class:`sphinx_hosting.models.SphinxPage`.
    It consists of a two column layout with the page's table of contents in the
    left column, and the content of the page in the right column.

    Args:
        page: the ``SphinxPage`` to render
    """

    left_column_width: int = 8

    def __init__(self, page: SphinxPage, **kwargs):
        super().__init__(**kwargs)
        self.add_block(SphinxPagePagination(page, css_class='mb-4'))
        self.add_block(SphinxPageTitle(page))
        layout = TwoColumnLayoutWidget(left_column_width=self.left_column_width)
        if page.local_toc:
            layout.add_to_right(SphinxPageTableOfContentsWidget(page))
        layout.add_to_left(SphinxPageBodyWidget(page))
        self.add_block(layout)
        self.add_block(SphinxPagePagination(page, css_class='mt-5'))
