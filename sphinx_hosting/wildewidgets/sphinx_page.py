from typing import Any, Dict, List, Optional  # noqa: UP035

from crequest.middleware import CrequestMiddleware
from django.template import Context, Template
from wildewidgets import (
    Block,
    CardHeader,
    CardWidget,
    Column,
    FontIcon,
    HTMLWidget,
    Link,
    LinkButton,
    Menu,
    MenuItem,
    Row,
    TwoColumnLayout,
)

from ..logging import logger
from ..models import SphinxPage, Version

# ------------------------------------------------------
# SphinxPage related widgets
# ------------------------------------------------------


class SphinxPagePagination(Row):
    """
    Draws the "Previous Page", Parent Page and Next Page buttons that
    are found at the top of each
    :py:class:`sphinx_hosting.views.SphinxPageDetailView`.

    It is built out of a Tabler/Bootstrap ``row``, with each of the buttons in
    an equal sized ``col``.
    """

    name: str = "sphinxpage-pagination"

    def __init__(self, page: SphinxPage, **kwargs):
        super().__init__(**kwargs)
        self.add_column(
            Column(name="left", alignment="start", viewport_widths={"md": "4"})
        )
        self.add_column(
            Column(name="center", alignment="center", viewport_widths={"md": "4"})
        )
        self.add_column(
            Column(name="right", alignment="end", viewport_widths={"md": "4"})
        )
        if hasattr(page, "previous_page") and page.previous_page.first():
            self.add_to_left(
                LinkButton(
                    text=Block(
                        FontIcon("box-arrow-in-left"), page.previous_page.first().title
                    ),
                    url=page.previous_page.first().get_absolute_url(),
                    name=f"{self.name}__previous",
                    css_class="bg-azure-lt",
                )
            )
        if page.parent:
            self.add_to_center(
                LinkButton(
                    text=Block(FontIcon("box-arrow-in-up"), page.parent.title),  # type: ignore[attr-defined]
                    url=page.parent.get_absolute_url(),  # type: ignore[attr-defined]
                    name=f"{self.name}__parent",
                    css_class="bg-azure-lt",
                )
            )
        if page.next_page:
            self.add_to_right(
                LinkButton(
                    text=Block(page.next_page.title, FontIcon("box-arrow-in-right")),  # type: ignore[attr-defined]
                    url=page.next_page.get_absolute_url(),  # type: ignore[attr-defined]
                    name=f"{self.name}__next",
                    css_class="bg-azure-lt",
                )
            )


class SphinxPagePermalinkWidget(CardWidget):
    """
    Draws the "Permalink" button that is found at the top of the
    right-hand column of each :py:class:`sphinx_hosting.views.SphinxPageDetailView`.

    Args:
        page: the ``SphinxPage`` we are rendering

    """

    def __init__(self, page: SphinxPage, **kwargs):
        super().__init__(**kwargs)
        self.page = page
        self.widget = Block(
            # This is the button that will be clicked to copy the permalink to the
            # clipboard.
            Link(
                FontIcon("share", css_class="me-2"),
                "Permalink",
                css_id="page-permalink",
                css_class="btn btn-outline-primary ms-auto",
            ),
            # This is the alert that will be displayed when the permalink is
            # successfully copied to the clipboard.  It starts hidden.
            Block(
                "Permalink copied to clipboard!",
                css_id="permalink-success-alert",
                css_class="alert alert-success mt-2",
                attributes={"role": "alert", "style": "display: none !important;"},
            ),
            css_class="d-flex flex-column",
        )

    def get_script(self) -> Optional[str]:  # noqa: FA100
        """
        Return the Javascript that will be executed when the "Permalink" button
        is clicked.  This will copy the permalink to the browser clipboard.

        Returns:
            The javascript for this block.

        """
        request = CrequestMiddleware.get_request()
        host = request.get_host()
        # nosemgrep: python.flask.security.audit.directly-returned-format-string.directly-returned-format-string  # noqa: E501, ERA001
        return f"""
$('#page-permalink').click(function() {{
    navigator.clipboard.writeText("https://{host}{self.page.get_permalink()}").then(
        () => {{
            $('#permalink-success-alert').show("slow");
            $('#permalink-success-alert').delay(3000).hide("slow");
        }},
        () => {{
            alert("Copy failed!");
        }}
    );
}});
"""


class SphinxPageBodyWidget(CardWidget):
    """
    The body of the page.  The body as stored in the model is
    actually a Django template, so we retrieve the body, run it through the
    Django template engine, and display the results.

    Args:
        page: the ``SphinxPage`` we are rendering

    """

    css_class: str = "sphinxpage-body"

    def __init__(self, page: SphinxPage, **kwargs):
        super().__init__(**kwargs)
        body = "{% load sphinx_hosting %}\n" + page.body
        self.widget = HTMLWidget(html=Template(body).render(Context()))


class SphinxPageTableOfContentsWidget(CardWidget):
    """
    Draws the in-page navigation -- the header hierarchy.

    Args:
        page: the ``SphinxPage`` we are rendering

    """

    css_class: str = "sphinxpage-toc"

    def __init__(self, page: SphinxPage, **kwargs):
        super().__init__(**kwargs)
        self.widget = HTMLWidget(html=page.local_toc)
        self.set_header(
            CardHeader(header_level=3, header_text="Table of Contents", css_class="")
        )


class SphinxPageGlobalTableOfContentsMenu(Menu):
    """
    The version-specific navigation menu that gets inserted into the
    page sidebar when viewing the documentation for a
    :py:class:`sphinx_hosting.models.Version`.  It will appear on all pages for
    that version.
    """

    css_class: str = "mt-4"
    title_css_classes: str = "mt-3"

    @classmethod
    def parse_obj(cls, version: Version) -> "SphinxPageGlobalTableOfContentsMenu":
        """
        Parse the globaltoc of a :py:class:`sphinx_hosting.models.Version` into
        a :py:class:`wildewidgets.Menu` suitable for insertion into a
        :py:class:`wildewidgets.Navbar`

        The :py:attr:`sphinx_hosting.models.Version.globaltoc` is a dict that
        looks like this::

            {
                items: [
                    {'text': 'foo'},
                    {'text': 'bar', 'url': '/foo', 'icon': 'blah'}
                    {'text': 'bar', 'url': '/foo', 'icon': 'blah', items: [{'text': 'blah' ...} ...]}
                    ...
                ]
            }

        Args:
            version: the ``Version`` for which we are building the menu

        Returns:
            A configured  ``SphinxPageGlobalTableOfContentsMenu``.

        """  # noqa: E501
        data = version.globaltoc
        menu_items = cls._load_menuitems(data["items"])
        if version.project.related_links.exists():  # type: ignore[attr-defined]
            link_items: List[MenuItem] = [MenuItem(text="Related Links")]
            for link in version.project.related_links.all():  # type: ignore[attr-defined]
                link_items.append(MenuItem(text=link.title, url=link.uri, icon="link"))  # noqa: PERF401
            if len(menu_items) == 1:
                # There's only a single page in this version, so we can
                # just extend the list of menu items with the link items
                menu_items.extend(link_items)
            else:
                if menu_items[1].url is not None and menu_items[1].items is not None:
                    # Insert a "Content" heading after the "Home" link
                    # to separate it from the links
                    menu_items.insert(1, MenuItem(text="Content"))
                link_items.reverse()
                for item in link_items:
                    menu_items.insert(1, item)
        if menu_items[0].text != "Home":
            # Let's be consistent about naming the top page of the
            # version "Home".  The globaltoc adds a Home link if there
            # isn't one, but those without globaltoc will have their
            # top page named after the project.
            menu_items[0].text = "Home"
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

        Return a list of :py:class:`wildewidgets.MenuItem`
        objects loaded from that data.

        Returns:
            A list of :py:class:`wildewidgets.MenuItem` objects.

        """  # noqa: E501
        menu_items: List[MenuItem] = []
        for item in items:
            if "items" in item:
                sub_items = cls._load_menuitems(item["items"])
                menu_items.append(
                    MenuItem(
                        text=item["text"],
                        url=item.get("url", None),
                        icon=item.get("icon", None),
                        items=sub_items,
                    )
                )
            else:
                menu_items.append(MenuItem(**item))
        return menu_items


class SphinxPageTitle(Block):
    """
    The title block for a :py:class:`sphinx_hosting.models.SphinxPage` page.

    Args:
        page: the ``SphinxPage`` to render

    """

    block: str = "sphinxpage-title"
    css_class: str = "mb-5"

    def __init__(self, page: SphinxPage, **kwargs):
        super().__init__(**kwargs)
        self.project_title = page.version.project.title  # type: ignore[attr-defined]
        self.version_number = page.version.version  # type: ignore[attr-defined]
        self.title = page.title
        self.add_block(
            Block(
                f"{self.project_title}-{self.version_number}",
                name="project-title",
                css_class="text-muted fs-6 text-uppercase",
            )
        )
        self.add_block(
            Block(
                self.title,
                tag="h1",
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
        self.add_block(SphinxPagePagination(page, css_class="mb-4"))
        self.add_block(SphinxPageTitle(page))
        layout = TwoColumnLayout(left_column_width=self.left_column_width)
        layout.add_to_right(SphinxPagePermalinkWidget(page))
        if page.local_toc:
            layout.add_to_right(SphinxPageTableOfContentsWidget(page))
        layout.add_to_left(SphinxPageBodyWidget(page))
        self.add_block(layout)
        self.add_block(SphinxPagePagination(page, css_class="mt-5"))
