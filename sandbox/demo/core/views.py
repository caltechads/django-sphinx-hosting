from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from wildewidgets import Widget, WidgetListLayout

from sphinx_hosting.logging import logger
from sphinx_hosting.views import SphinxHostingMenuMixin, WildewidgetsMixin
from sphinx_hosting.wildewidgets import SphinxHostingBreadcrumbs

from .forms import SearchNoteForm
from .models import SearchNote
from .wildewidgets import (
    SearchNoteDetailWidget,
    SearchNoteFormWidget,
    SearchNoteListWidget,
)

if TYPE_CHECKING:
    from django.db.models import Model
    from django.http import HttpRequest, HttpResponse


class SearchNoteListView(  # type: ignore[misc]
    LoginRequiredMixin, WildewidgetsMixin, SphinxHostingMenuMixin, ListView
):
    """
    Render the demo landing page for browsing ``SearchNote`` records.
    """

    #: Menu item activated in the shared sphinx-hosting sidebar.
    menu_item: str = "Search Notes"
    #: Model displayed by the list page.
    model = SearchNote

    def get_queryset(self):
        """
        Return notes with related objects eager loaded for the list page.

        Returns:
            Ordered queryset for the list template.

        """
        return (
            SearchNote.objects.select_related("project")
            .prefetch_related("classifiers")
            .order_by("title")
        )

    def get_content(self) -> Widget:
        """
        Build the widget layout for the SearchNote list page.

        Returns:
            Populated widget layout for the page shell.

        """
        layout = WidgetListLayout("Search Notes")
        layout.add_widget(SearchNoteListWidget(self.get_queryset()))
        layout.add_sidebar_link_button(
            "Create Search Note",
            reverse("core:searchnote--create"),
            color="azure",
        )
        return layout

    def get_breadcrumbs(self) -> SphinxHostingBreadcrumbs:
        """
        Build breadcrumbs for the SearchNote list page.

        Returns:
            Breadcrumb trail for the list page.

        """
        breadcrumbs = SphinxHostingBreadcrumbs()
        breadcrumbs.add_breadcrumb("Search Notes")
        return breadcrumbs


class SearchNoteDetailView(  # type: ignore[misc]
    LoginRequiredMixin, WildewidgetsMixin, SphinxHostingMenuMixin, DetailView
):
    """
    Render one demo ``SearchNote`` record with its related metadata.
    """

    #: Menu item activated in the shared sphinx-hosting sidebar.
    menu_item: str = "Search Notes"
    #: Model displayed by the detail page.
    model = SearchNote

    def get_queryset(self):
        """
        Return notes with related project and classifier data loaded.

        Returns:
            Queryset used by the detail view.

        """
        return SearchNote.objects.select_related("project").prefetch_related(
            "classifiers"
        )

    def get_content(self) -> Widget:
        """
        Build the widget layout for one SearchNote detail page.

        Returns:
            Populated widget layout for the page shell.

        """
        layout = WidgetListLayout(self.object.title)
        layout.add_widget(SearchNoteDetailWidget(self.object))
        layout.add_sidebar_link_button(
            "Edit Search Note",
            self.object.get_update_url(),
            color="azure",
            css_class="mb-2",
        )
        layout.add_sidebar_link_button(
            "View Project",
            self.object.get_project_url(),
            color="orange",
            css_class="mb-2",
        )
        layout.add_sidebar_form_button(
            "Delete Application",
            reverse("core:searchnote--delete", args=[self.object.pk]),
            color="outline-secondary",
            confirm_text="Are you sure you want to delete this note?",
        )
        return layout

    def get_breadcrumbs(self) -> SphinxHostingBreadcrumbs:
        """
        Build breadcrumbs for the SearchNote detail page.

        Returns:
            Breadcrumb trail for the detail page.

        """
        breadcrumbs = SphinxHostingBreadcrumbs()
        breadcrumbs.add_breadcrumb(
            "Search Notes",
            url=reverse("core:searchnote--list"),
        )
        breadcrumbs.add_breadcrumb(self.object.title)
        return breadcrumbs


class SearchNoteCreateView(  # type: ignore[misc]
    LoginRequiredMixin, WildewidgetsMixin, SphinxHostingMenuMixin, CreateView
):
    """
    Create a new demo ``SearchNote`` record.
    """

    #: Menu item activated in the shared sphinx-hosting sidebar.
    menu_item: str = "Search Notes"
    #: Model created by this view.
    model = SearchNote
    #: Form used to collect note data.
    form_class = SearchNoteForm

    def get_form_kwargs(self) -> dict[str, Any]:
        """
        Inject the current form action URL into the model form.

        Returns:
            Keyword arguments for ``SearchNoteForm``.

        """
        kwargs = super().get_form_kwargs()
        kwargs["form_action"] = self.request.path
        return kwargs

    def get_content(self) -> Widget:
        """
        Build the widget layout for the SearchNote create page.

        Returns:
            Populated widget layout for the page shell.

        """
        layout = WidgetListLayout("Create Search Note")
        layout.add_widget(SearchNoteFormWidget(form=self.get_form()))
        return layout

    def get_breadcrumbs(self) -> SphinxHostingBreadcrumbs:
        """
        Build breadcrumbs for the SearchNote create page.

        Returns:
            Breadcrumb trail for the create page.

        """
        breadcrumbs = SphinxHostingBreadcrumbs()
        breadcrumbs.add_breadcrumb(
            "Search Notes",
            url=reverse("core:searchnote--list"),
        )
        breadcrumbs.add_breadcrumb("Create Search Note")
        return breadcrumbs


class SearchNoteUpdateView(  # type: ignore[misc]
    LoginRequiredMixin, WildewidgetsMixin, SphinxHostingMenuMixin, UpdateView
):
    """
    Update an existing demo ``SearchNote`` record.
    """

    #: Menu item activated in the shared sphinx-hosting sidebar.
    menu_item: str = "Search Notes"
    #: Model updated by this view.
    model = SearchNote
    #: Form used to edit note data.
    form_class = SearchNoteForm

    def get_form_kwargs(self) -> dict[str, Any]:
        """
        Inject the current form action URL into the model form.

        Returns:
            Keyword arguments for ``SearchNoteForm``.

        """
        kwargs = super().get_form_kwargs()
        kwargs["form_action"] = self.request.path
        return kwargs

    def get_content(self) -> Widget:
        """
        Build the widget layout for the SearchNote update page.

        Returns:
            Populated widget layout for the page shell.

        """
        layout = WidgetListLayout("Edit Search Note")
        layout.add_widget(SearchNoteFormWidget(form=self.get_form()))
        layout.add_sidebar_link_button(
            "View Search Note",
            self.object.get_absolute_url(),
            color="orange",
        )
        return layout

    def get_breadcrumbs(self) -> SphinxHostingBreadcrumbs:
        """
        Build breadcrumbs for the SearchNote update page.

        Returns:
            Breadcrumb trail for the update page.

        """
        breadcrumbs = SphinxHostingBreadcrumbs()
        breadcrumbs.add_breadcrumb(
            "Search Notes",
            url=reverse("core:searchnote--list"),
        )
        breadcrumbs.add_breadcrumb(
            self.object.title,
            url=self.object.get_absolute_url(),
        )
        breadcrumbs.add_breadcrumb("Edit Search Note")
        return breadcrumbs


class SearchNoteDeleteView(  # type: ignore[misc]
    LoginRequiredMixin, WildewidgetsMixin, SphinxHostingMenuMixin, DeleteView
):
    """
    Confirm and delete an existing demo ``SearchNote`` record.
    """

    #: Menu item activated in the shared sphinx-hosting sidebar.
    menu_item: str = "Search Notes"
    #: Model deleted by this view.
    model: type[Model] = SearchNote
    #: Redirect target after a successful delete.
    success_url: str = reverse_lazy("core:searchnote--list")
    #: Whether to raise exceptions for permission errors
    raise_exception: bool = True

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:  # noqa: ARG002
        """
        Delete a search note and redirect to the list page.

        Args:
            request: The HTTP request.
            *args: Additional positional arguments.

        Keyword Args:
            **kwargs: Additional keyword arguments.

        Returns:
            HttpResponseRedirect: Redirect to the home page.

        """
        self.object = self.get_object()
        # This bit check of whether the app is Operations is why we have to
        # rewrite all of DeleteView.delete():
        self.object.delete()
        logger.info("note.delete.success note_id=%s", self.object.pk)
        messages.success(
            request, f"Note '{self.object.title}' was successfully deleted."
        )
        return HttpResponseRedirect(self.get_success_url())
