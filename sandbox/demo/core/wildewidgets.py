from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from django.urls import reverse
from wildewidgets import (
    Block,
    CardWidget,
    CrispyFormWidget,
    Datagrid,
    DatagridItem,
    Link,
    StaticTableWidget,
)

from sphinx_hosting.wildewidgets import SphinxHostingSidebar

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser
    from django.db.models import QuerySet
    from django.forms import Form
    from django.http.request import HttpRequest
    from wildewidgets import WidgetListLayout

    from sphinx_hosting.models import Project
    from sphinx_hosting.views import ProjectDetailView
    from sphinx_hosting.wildewidgets import SphinxHostingMainMenu

    from .models import SearchNote

# ------------------------------------------------------
# Menus
# ------------------------------------------------------


def build_search_notes_menu_item(
    *, request: HttpRequest, user: AbstractUser, menu: SphinxHostingMainMenu
) -> dict[str, Any]:
    """
    Return a demo note-browser link for conditional menu-builder integration.

    Keyword Args:
        request: The current Django request.
        user: The authenticated user for this request.
        menu: The ``SphinxHostingMainMenu`` instance being built.

    Returns:
        A dictionary menu item specification.

    """
    del request, user, menu
    return {
        "text": "Search Notes",
        "icon": "journal-text",
        "url": reverse("core:searchnote--list"),
    }


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
        color="orange",
        css_class="mt-2",
    )


class MainMenu(SphinxHostingSidebar):
    """
    Demo override class for ``SPHINX_HOSTING_SETTINGS['NAVBAR_CLASS']`` tests.
    """


class SearchNoteListWidget(StaticTableWidget):
    """
    Render the main content block for the SearchNote list page.

    Args:
        notes: Queryset of notes to display.

    """

    #: The card title shown above the note list.
    title: str = "Search Notes"
    #: The bootstrap icon used in the card header.
    icon: str = "journal-text"

    def __init__(self, notes: QuerySet[SearchNote], **kwargs: Any) -> None:
        super().__init__(cell_css_class="p-3", **kwargs)
        self.notes = notes
        self.add_heading("Title")
        self.add_heading("Project")
        self.add_heading("Classifiers")
        self.add_heading("Created")
        self.add_heading("Last updated")
        for note in notes:
            self.add_row(
                [
                    Link(
                        note.title,
                        url=note.get_absolute_url(),
                    ),
                    Link(
                        cast("Project", note.project).title,
                        url=cast("Project", note.project).get_absolute_url(),
                    ),
                    "<br>".join(
                        [classifier.name for classifier in note.classifiers.all()]
                    ),
                    note.created.strftime("%Y-%m-%d %H:%M:%S"),
                    note.modified.strftime("%Y-%m-%d %H:%M:%S"),
                ]
            )


class SearchNoteDetailWidget(CardWidget):
    """
    Render the main content block for one SearchNote detail page.

    Args:
        note: Note instance displayed on the page.

    """

    #: The card title shown above the note detail.
    title: str = "Search Note"
    #: The bootstrap icon used in the card header.
    icon: str = "info-circle"

    def __init__(self, note: SearchNote, **kwargs: Any) -> None:
        """
        Store the note displayed by the widget.

        Args:
            note: Note instance displayed on the page.

        Keyword Args:
            **kwargs: Keyword arguments forwarded to ``CardWidget``.

        """
        datagrid = Datagrid(
            DatagridItem(
                cast("Project", note.project).title,
                title="Project",
                url=cast("Project", note.project).get_absolute_url(),
            ),
            DatagridItem(
                "<br>".join([classifier.name for classifier in note.classifiers.all()]),
                title="Classifiers",
            ),
            DatagridItem(
                note.created.strftime("%Y-%m-%d %H:%M:%S"),
                title="Created",
            ),
            DatagridItem(
                note.modified.strftime("%Y-%m-%d %H:%M:%S"),
                title="Last updated",
            ),
        )
        _note = Block(
            note.body,
            css_class="my-3 rounded-4 p-3 bg-gray-500",
        )
        #: Note instance rendered in the detail page.
        super().__init__(widget=Block(datagrid, _note), **kwargs)


class SearchNoteFormWidget(CardWidget):
    """
    Render the main content block for SearchNote create and update pages.

    Args:
        form: Bound or unbound form for the page.
        page_title: Heading shown above the form.
        cancel_url: Link back to the SearchNote list page.

    """

    #: The card title shown above the note form.
    title: str = "Search Note"
    #: The bootstrap icon used in the card header.
    icon: str = "pencil"

    def __init__(self, form: Form, **kwargs: Any) -> None:
        """
        Store the form and labels used by the form widget.

        Args:
            form: Bound or unbound form for the page.

        Keyword Args:
            **kwargs: Keyword arguments forwarded to ``CardWidget``.

        """
        #: Bound or unbound form rendered by the widget.
        self.form = form
        super().__init__(widget=CrispyFormWidget(form=form), **kwargs)
