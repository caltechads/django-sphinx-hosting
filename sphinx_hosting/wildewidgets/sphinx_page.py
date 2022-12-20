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
    are found at the top of each :py:class:`sphinx_hosting.views.SphinxPageDetailView`.

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
                    text=Block(
                        FontIcon('box-arrow-in-left'),
                        page.previous_page.first().title
                    ),
                    url=page.previous_page.first().get_absolute_url(),
                    name=f'{self.name}__previous',
                    css_class='bg-azure bg-azure-fg'
                )
            )
        if page.parent:
            self.add_to_center(
                LinkButton(
                    text=Block(
                        FontIcon('box-arrow-in-up'),
                        page.parent.title
                    ),
                    url=page.parent.get_absolute_url(),
                    name=f'{self.name}__parent',
                    css_class='bg-azure bg-azure-fg'
                )
            )
        if page.next_page:
            self.add_to_right(
                LinkButton(
                    text=Block(
                        page.next_page.title,
                        FontIcon('box-arrow-in-right')
                    ),
                    url=page.next_page.get_absolute_url(),
                    name=f'{self.name}__next',
                    css_class='bg-azure bg-azure-fg'
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


class SphinxPageLayout(Block):
    """
    The page layout for a single :py:class:`sphinx_hosting.models.SphinxPage`.
    It consists of a two column layout with the page's table of contents in the
    left column, and the content of the page in the right column.

    Args:
        page: the ``SphinxPage`` to render
    """

    left_column_width: int = 4

    def __init__(self, page: SphinxPage, **kwargs):
        super().__init__(**kwargs)
        self.add_block(SphinxPagePagination(page, css_class='mb-5'))
        layout = TwoColumnLayoutWidget(left_column_width=self.left_column_width)
        layout.add_to_left(SphinxPageTableOfContentsWidget(page))
        if page.version.global_toc:
            layout.add_to_left(SphinxPageGlobalTableOfContentsWidget(page))
        layout.add_to_right(SphinxPageBodyWidget(page))
        self.add_block(layout)
        self.add_block(SphinxPagePagination(page, css_class='mt-5'))
