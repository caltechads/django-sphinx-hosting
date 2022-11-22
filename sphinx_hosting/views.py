from typing import Type, cast

from braces.views import (
    FormInvalidMessageMixin,
    FormValidMessageMixin,
    LoginRequiredMixin,
)
from django.contrib import messages
from django.db.models import Model, QuerySet
from django.forms import ModelForm
from django.http import HttpResponse, HttpRequest
from django.shortcuts import redirect
from django.utils.translation import gettext as _
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    TemplateView,
    UpdateView
)

from wildewidgets import (
    BasicMenu,
    MenuMixin,
    StandardWidgetMixin,
    WidgetListLayout,
    Widget
)

from .forms import (
    ProjectCreateForm,
    ProjectUpdateForm
)
from .logging import logger
from .models import (
    Project,
    Version,
    SphinxPage
)
from .wildewidgets import (
    ProjectCreateModalWidget,
    ProjectDetailWidget,
    ProjectInfoWidget,
    ProjectVersionsTableWidget,
    ProjectTableWidget,
    SphinxHostingMenu,
    SphinxHostingBreadcrumbs,
    SphinxPageLayout,
    SphinxPagePagination,
    VersionInfoWidget,
    VersionSphinxPageTableWidget
)


# ===========================
# View Mixins
# ===========================

class WildewidgetsMixin(StandardWidgetMixin):
    """
    We subclass :py:class:`WildewidgetsMixin` here so that we can define our
    standard template.
    """
    template_name = 'sphinx_hosting/base.html'


# ===========================
# Projects
# ===========================


class ProjectListView(
    LoginRequiredMixin,
    MenuMixin,
    WildewidgetsMixin,
    TemplateView
):
    """
    This is the view we use for the home page of the ``sphinx_hosting`` app.  It
    lists all available :py:class:`sphinx_hosting.models.Project` objects from
    the database and allows the user to create new Projects.
    """
    menu_class = SphinxHostingMenu
    menu_item = "Projects"

    def get_content(self) -> Widget:
        layout = WidgetListLayout("Projects")
        layout.add_widget(ProjectTableWidget())
        layout.add_modal(ProjectCreateModalWidget())
        return layout

    def get_breadcrumbs(self) -> SphinxHostingBreadcrumbs:
        breadcrumbs = SphinxHostingBreadcrumbs()
        return breadcrumbs


class ProjectCreateView(
    LoginRequiredMixin,
    FormInvalidMessageMixin,
    FormValidMessageMixin,
    CreateView
):
    """
    This is a POST only view for creating a
    :py:class:`sphinx_hosting.models.Project`.  The POST will be submitted from
    the "Add Project" modal form displayed on :py:class:`ProjectListView`.
    """
    model: Type[Model] = Project
    form_class: Type[ModelForm] = ProjectCreateForm

    def get_form_valid_message(self) -> str:
        obj = cast(Project, self.object)
        return f'Added Project "{obj.title}"'

    def form_invalid(self, form: ModelForm) -> HttpResponse:
        for k, errors in form.errors.as_data().items():
            for error in errors:
                messages.error(self.request, f"{k}: {error.message}")
        return redirect('sphinx_hosting:project--list')

    def get_success_url(self) -> str:
        obj = cast(Project, self.object)
        logger.info("project.create.success project=%s id=%s", obj.machine_name, obj.id)
        return reverse('sphinx_hosting:project--update', args=[obj.id])

    def get_form_invalid_message(self) -> str:
        logger.warning('project.create.failed.validation')
        return _("Couldn't create this project due to validation errors; see below.")


class ProjectUpdateView(
    LoginRequiredMixin,
    FormValidMessageMixin,
    WildewidgetsMixin,
    MenuMixin,
    UpdateView
):
    """
    This view handles displaying the details page for a
    :py:class:`sphinx_hosting.models.Project` and handles updates to the project
    settings itself.
    """

    menu_class: Type[BasicMenu] = SphinxHostingMenu
    menu_item: str = "Projects"
    model: Type[Model] = Project
    form_class: Type[ModelForm] = ProjectUpdateForm
    slug_field: str = 'machine_name'

    def get_content(self) -> Widget:
        layout = WidgetListLayout(self.object.title)
        layout.add_widget(ProjectInfoWidget(self.object))
        layout.add_widget(ProjectDetailWidget(self.object))
        layout.add_widget(ProjectVersionsTableWidget(project_id=self.object.pk))
        layout.add_sidebar_form_button(
            'Delete Project',
            reverse('sphinx_hosting:project--delete', args=[self.object.pk]),
            color='outline-secondary',
            confirm_text=_("Are you sure you want to delete this project?"),
        )
        return layout

    def get_breadcrumbs(self) -> SphinxHostingBreadcrumbs:
        breadcrumbs = SphinxHostingBreadcrumbs()
        breadcrumbs.add_breadcrumb(self.object.machine_name)
        return breadcrumbs

    def get_form_valid_message(self) -> str:
        return f'Updated Project "{self.object.title}"'

    def get_success_url(self) -> str:
        logger.info('project.update.success project=%s id=%s', self.object.machine_name, self.object.id)
        return reverse('sphinx_hosting:project--update', args=[self.object.pk])


class ProjectDeleteView(
    LoginRequiredMixin,
    DeleteView
):
    model: Type[Model] = Project
    success_url = reverse_lazy('sphinx_hosting:project--list')
    slug_field: str = 'machine_name'

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        response = super().delete(request, *args, **kwargs)
        logger.info(
            "project.delete.success project=%s id=%s",
            self.object.machine_name,
            self.object.pk
        )
        return response


# ===========================
# Versions
# ===========================


class VersionDetailView(
    LoginRequiredMixin,
    WildewidgetsMixin,
    MenuMixin,
    DetailView
):
    """
    This view handles displaying the details page for a
    :py:class:`sphinx_hosting.models.Project` and handles updates to the project
    settings itself.
    """

    menu_class: Type[BasicMenu] = SphinxHostingMenu
    menu_item: str = "Projects"
    model: Type[Model] = Version
    slug_field: str = 'version'
    slug_url_kwarg: str = 'version'

    def get_queryset(self) -> QuerySet[Version]:
        """
        Pre-filter our default queryset so that we only are able to get
        :py:class:`sphinx_hosting.models.Version` objects associated with the
        :py:class:`sphinx_hosting.models.Project` identified by our
        ``project_slug`` URLPath kwarg.

        Parameters:
            project_slug: the :py:attr:`sphinx_hosting.models.Project.machine_name`
                of our project

        Returns:
            A queryset of ``Version`` objects filtered by ``project_slug``
        """
        project_machine_name = self.kwargs.get('project_slug', None)
        return super().get_queryset().filter(project__machine_name=project_machine_name)

    def get_content(self) -> Widget:
        layout = WidgetListLayout(f'{self.object.project.title} {self.object.version}')
        layout.add_widget(VersionInfoWidget(self.object))
        layout.add_widget(VersionSphinxPageTableWidget(version_id=self.object.pk))
        if self.object.head:
            layout.add_sidebar_link_button(
                'Read Docs',
                reverse(
                    'sphinx_hosting:sphinxpage--detail',
                    args=[
                        self.object.project.pk,
                        self.object.version,
                        self.object.head.relative_path
                    ]
                ),
            )
        layout.add_sidebar_form_button(
            'Delete Version',
            reverse('sphinx_hosting:version--delete', args=[self.object.project.pk, self.object.version]),
            color='outline-secondary',
            confirm_text=_("Are you sure you want to delete this version?"),
        )
        return layout

    def get_breadcrumbs(self) -> SphinxHostingBreadcrumbs:
        breadcrumbs = SphinxHostingBreadcrumbs()
        breadcrumbs.add_breadcrumb(self.object.project.machine_name, url=self.object.project.get_absolute_url())
        breadcrumbs.add_breadcrumb(self.object.version)
        return breadcrumbs


class VersionDeleteView(
    LoginRequiredMixin,
    DeleteView
):
    model: Type[Model] = Version
    slug_field: str = 'version'
    slug_url_kwarg: str = 'version'

    def get_queryset(self) -> QuerySet[Version]:
        """
        Pre-filter our default queryset so that we only are able to get
        :py:class:`sphinx_hosting.models.Version` objects associated with the
        :py:class:`sphinx_hosting.models.Project` identified by our
        ``project_slug`` URLPath kwarg.

        Parameters:
            project_slug: the :py:attr:`sphinx_hosting.models.Project.machine_name`
                of our project

        Returns:
            A queryset of ``Version`` objects filtered by ``project_slug``
        """
        project_machine_name = self.kwargs.get('project_slug', None)
        return super().get_queryset().filter(project__machine_name=project_machine_name)

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        response = super().delete(request, *args, **kwargs)
        logger.info("version.delete.success project=%s id=%s", self.object.machine_name, self.object.pk)
        return response

    def get_success_url(self) -> str:
        return reverse('sphinx_hosting:project--update', args=[self.kwargs['project_id']])


# ===========================
# Pages
# ===========================

class SphinxPageDetailView(
    LoginRequiredMixin,
    WildewidgetsMixin,
    MenuMixin,
    DetailView
):
    """
    This view handles displaying the actual contents of the
    :py:class:`SphinxPage`, with navigation, table of contents and the actual
    page content.
    """

    menu_class: Type[BasicMenu] = SphinxHostingMenu
    menu_item: str = "Projects"
    model: Type[Model] = SphinxPage
    slug_field: str = 'relative_path'
    slug_url_kwarg: str = 'path'

    def get_submenu(self) -> SphinxPagePagination:
        """
        Configure our per-page pagination menu.  This is what shows the "Up",
        "Prev" and "Next" links at the top of the page.

        Returns:
            A submenu configured specifically for this page.
        """
        return SphinxPagePagination(self.object)

    def get_queryset(self) -> QuerySet[SphinxPage]:
        """
        Pre-filter our default queryset so that we only are able to get
        :py:class:`sphinx_hosting.models.SphinxPage` objects associated with the
        :py:class:`sphinx_hosting.models.Version` identified by our ``project_slug``
        and ``version`` URLPath kwargs:

        Parameters:
            project_slug: the :py:attr:`sphinx_hosting.models.Project.machine_name`
                of our project
            version: the :py:attr:`sphinx_hosting.models.Version.version` string
                of our version

        Returns:
            A queryset of ``SphinxPage`` objects filtered to a particular version of
            a particular project.
        """
        project_id = self.kwargs.get('project_id', None)
        version = self.kwargs.get('version', None)
        return super().get_queryset().filter(version__version=version, version__project_id=project_id)

    def get_content(self) -> Widget:
        return SphinxPageLayout(self.object)

    def get_breadcrumbs(self):
        breadcrumbs = SphinxHostingBreadcrumbs()
        breadcrumbs.add_breadcrumb(
            self.object.version.project.machine_name,
            url=self.object.version.project.get_absolute_url()
        )
        breadcrumbs.add_breadcrumb(self.object.version.version, url=self.object.version.get_absolute_url())
        breadcrumbs.add_breadcrumb(self.object.title)
        return breadcrumbs
