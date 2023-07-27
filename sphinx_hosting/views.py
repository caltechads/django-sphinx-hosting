import os
import tempfile
from typing import Dict, List, Optional, Type, cast

from braces.views import (
    FormInvalidMessageMixin,
    FormValidMessageMixin,
    LoginRequiredMixin,
    MessageMixin,
    PermissionRequiredMixin,
)
from django.contrib import messages
from django.contrib.auth.models import AbstractUser
from django.core.files.storage import FileSystemStorage
from django.db.models import Model, QuerySet
from django.forms import ModelForm, Form
from django.http import HttpResponse, HttpRequest, Http404
from django.shortcuts import redirect, get_object_or_404
from django.utils.translation import gettext as _
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import (
    BaseFormView,
    BaseCreateView,
    BaseUpdateView
)
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    TemplateView,
    UpdateView
)
from haystack.forms import ModelSearchForm
from haystack.query import SearchQuerySet
from haystack.generic_views import SearchView
from wildewidgets import (
    Navbar,
    NavbarMixin,
    StandardWidgetMixin,
    WidgetListLayout,
    Widget,
    WidgetStream
)
from wildewidgets.viewsets import ModelViewSet

from .forms import (
    ProjectCreateForm,
    ProjectUpdateForm,
    ProjectReadonlyUpdateForm,
    ProjectRelatedLinkCreateForm,
    ProjectRelatedLinkUpdateForm,
    VersionUploadForm
)
from .importers import SphinxPackageImporter
from .logging import logger
from .models import (
    Classifier,
    Project,
    ProjectRelatedLink,
    Version,
    SphinxPage
)

from .wildewidgets import (
    ProjectClassifierListWidget,
    ProjectClassifierSelectorWidget,
    ProjectCreateModalWidget,
    ProjectDetailWidget,
    ProjectInfoWidget,
    ProjectRelatedLinkCreateModalWidget,
    ProjectRelatedLinksWidget,
    ProjectRelatedLinksListWidget,
    ProjectVersionsTableWidget,
    ProjectTableWidget,
    PagedSearchLayout,
    SphinxPageGlobalTableOfContentsMenu,
    SphinxHostingBreadcrumbs,
    SphinxHostingSidebar,
    SphinxPageLayout,
    VersionInfoWidget,
    VersionSphinxPageTableWidget,
    VersionSphinxImageTableWidget,
    VersionUploadBlock,
)

# ===========================
# Viewsets
# ===========================


class ClassifierViewSet(ModelViewSet):
    model = Classifier
    template_name = 'sphinx_hosting/base.html'
    breadcrumbs_class = SphinxHostingBreadcrumbs
    navbar_class = SphinxHostingSidebar


# ===========================
# View Mixins
# ===========================

class SphinxHostingMenuMixin(NavbarMixin):

    navbar_class: Type[Navbar] = SphinxHostingSidebar


class WildewidgetsMixin(StandardWidgetMixin):  # pylint: disable=abstract-method
    """
    We subclass :py:class:`wildewidgets.StandardWidgetMixin` here so that we can define our
    standard template.
    """
    template_name = 'sphinx_hosting/base.html'


# ===========================
# Projects
# ===========================


class ProjectListView(
    LoginRequiredMixin,
    WildewidgetsMixin,
    SphinxHostingMenuMixin,
    TemplateView
):
    """
    This is the view we use for the home page of the ``sphinx_hosting`` app.  It
    lists all available :py:class:`sphinx_hosting.models.Project` objects from
    the database and allows the user to create new Projects.
    """
    menu_item: str = 'Projects'

    def get_content(self) -> Widget:
        layout = WidgetStream()
        user = cast(AbstractUser, self.request.user)
        layout.add_widget(ProjectTableWidget(user))
        if user.has_perm('sphinxhostingcore.add_project'):
            layout.add_widget(ProjectCreateModalWidget())
        return layout

    def get_breadcrumbs(self) -> SphinxHostingBreadcrumbs:
        breadcrumbs = SphinxHostingBreadcrumbs()
        return breadcrumbs


class ProjectDetailView(
    LoginRequiredMixin,
    WildewidgetsMixin,
    SphinxHostingMenuMixin,
    DetailView
):
    """
    This view handles displaying the details page for a
    :py:class:`sphinx_hosting.models.Project` and handles updates to the project
    settings itself.
    """

    menu_item: str = "Projects"

    model: Type[Model] = Project
    slug_field: str = 'machine_name'

    def get_content(self) -> Widget:
        layout = WidgetListLayout(self.object.title)
        layout.add_widget(ProjectInfoWidget(self.object))
        layout.add_widget(
            ProjectDetailWidget(
                self.object,
                form=ProjectReadonlyUpdateForm(instance=self.object)
            )
        )
        layout.add_widget(ProjectRelatedLinksListWidget(queryset=self.object.related_links.all()))
        layout.add_widget(ProjectClassifierListWidget(queryset=self.object.classifiers.all()))
        layout.add_widget(ProjectVersionsTableWidget(project_id=self.object.pk))
        user = cast(AbstractUser, self.request.user)
        version = self.object.latest_version
        if version and version.head:
            layout.add_sidebar_link_button(
                'Read Docs',
                reverse(
                    'sphinx_hosting:sphinxpage--detail',
                    args=[
                        self.object.machine_name,
                        version.version,
                        version.head.relative_path
                    ]
                ),
                color='orange',
                css_class='mb-3'
            )
        if user.has_perm('sphinxhostingcore.change_project'):
            layout.add_sidebar_link_button(
                'Edit Project',
                reverse('sphinx_hosting:project--update', args=[self.object.machine_name]),
                color='azure',
            )
        return layout

    def get_breadcrumbs(self) -> SphinxHostingBreadcrumbs:
        breadcrumbs = SphinxHostingBreadcrumbs()
        breadcrumbs.add_breadcrumb(self.object.title)
        return breadcrumbs


class ProjectCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    FormInvalidMessageMixin,
    FormValidMessageMixin,
    CreateView
):
    """
    This is a POST only view for creating a
    :py:class:`sphinx_hosting.models.Project`.  The POST will be submitted from
    the "Add Project" modal form displayed on :py:class:`ProjectListView`.
    """
    permission_required: str = 'sphinxhostingcore.add_project'
    model: Type[Model] = Project
    form_class: Type[ModelForm] = ProjectCreateForm

    def get_form_valid_message(self) -> str:
        obj = cast(Project, self.object)
        return f'Added Project "{obj.title}"'

    def form_invalid(self, form: ModelForm) -> HttpResponse:
        """
        If the form is invalid, we want to display the errors to the user and
        redirect them back to the project list page.

        Args:
            form: The form that was submitted

        Returns:
            The redirect response
        """
        for k, errors in form.errors.as_data().items():
            for error in errors:
                messages.error(self.request, f"{k}: {error.message}")
        return redirect('sphinx_hosting:project--list')

    def get_success_url(self) -> str:
        obj = cast(Project, self.object)
        logger.info("project.create.success project=%s id=%s", obj.machine_name, obj.id)
        return reverse('sphinx_hosting:project--update', args=[obj.machine_name])

    def get_form_invalid_message(self) -> str:
        logger.warning('project.create.failed.validation')
        return _("Couldn't create this project due to validation errors; see below.")


class ProjectUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    FormValidMessageMixin,
    WildewidgetsMixin,
    SphinxHostingMenuMixin,
    UpdateView
):
    """
    This view handles displaying the details page for a
    :py:class:`sphinx_hosting.models.Project` and handles updates to the project
    settings itself.
    """

    menu_item: str = "Projects"

    permission_required: str = 'sphinxhostingcore.change_project'
    model: Type[Model] = Project
    form_class: Type[ModelForm] = ProjectUpdateForm
    slug_field: str = 'machine_name'

    def get_content(self) -> Widget:
        layout = WidgetListLayout(self.object.title)
        layout.add_widget(ProjectInfoWidget(self.object))
        layout.add_widget(ProjectDetailWidget(self.object))
        layout.add_widget(ProjectRelatedLinksWidget(self.object))
        layout.add_widget(ProjectClassifierSelectorWidget(self.object))
        layout.add_widget(ProjectVersionsTableWidget(project_id=self.object.pk))
        layout.add_widget(ProjectRelatedLinkCreateModalWidget(self.object))
        version = self.object.latest_version
        user = cast(AbstractUser, self.request.user)
        if version and version.head:
            layout.add_sidebar_link_button(
                'Read Docs',
                reverse(
                    'sphinx_hosting:sphinxpage--detail',
                    args=[
                        self.object.machine_name,
                        version.version,
                        version.head.relative_path
                    ]
                ),
                color='orange',
                css_class='mb-3'
            )
        if user.has_perm('sphinxhostingcore.change_project'):
            layout.add_sidebar_bare_widget(
                VersionUploadBlock(form=VersionUploadForm(project=self.object))
            )
        if user.has_perm('sphinxhostingcore.delete_project'):
            layout.add_sidebar_form_button(
                'Delete Project',
                reverse('sphinx_hosting:project--delete', args=[self.object.machine_name]),
                color='outline-secondary',
                confirm_text=_("Are you sure you want to delete this project?"),
            )
        return layout

    def get_breadcrumbs(self) -> SphinxHostingBreadcrumbs:
        breadcrumbs = SphinxHostingBreadcrumbs()
        breadcrumbs.add_breadcrumb(self.object.title)
        return breadcrumbs

    def get_form_valid_message(self) -> str:
        return f'Updated Project "{self.object.title}"'

    def get_success_url(self) -> str:
        logger.info('project.update.success project=%s id=%s', self.object.machine_name, self.object.id)
        return reverse('sphinx_hosting:project--update', args=[self.object.machine_name])


class ProjectDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    DeleteView
):
    model: Type[Model] = Project
    permission_required: str = 'sphinxhostingcore.delete_project'
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
# ProjectRelatedLinks
# ===========================

class ProjectRelatedLinkCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    FormValidMessageMixin,
    BaseCreateView
):
    form_class = ProjectRelatedLinkCreateForm
    model: Type[Model] = ProjectRelatedLink
    permission_required: str = 'sphinxhostingcore.change_project'

    def get_form_kwargs(self) -> Dict[str, str]:
        self.project: Project = get_object_or_404(Project, machine_name=self.kwargs['project_slug'])
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.project
        return kwargs

    def form_valid(self, form: Form) -> HttpResponse:
        form.instance.project = self.project  # type: ignore
        return super().form_valid(form)

    def get_form_valid_message(self) -> str:
        link = cast(ProjectRelatedLink, self.object)
        return f'Created Related Link "{link.title}" for project "{link.project.machine_name}"'

    def get_success_url(self) -> str:
        link = cast(ProjectRelatedLink, self.object)
        logger.info(
            'project.relatedlink.create.success project=%s link_id=%s link_title=%s link_url=%s',
            link.project.machine_name,
            link.id,
            link.title,
            link.uri
        )
        return reverse('sphinx_hosting:project--update', args=[link.project.machine_name])


class ProjectRelatedLinkUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    FormValidMessageMixin,
    BaseUpdateView
):
    form_class = ProjectRelatedLinkUpdateForm
    model: Type[Model] = ProjectRelatedLink
    permission_required: str = 'sphinxhostingcore.change_project'

    def get_form_kwargs(self) -> Dict[str, str]:
        kwargs = super().get_form_kwargs()
        kwargs['project_machine_name'] = self.object.project.machine_name
        return kwargs

    def get_form_valid_message(self) -> str:
        return f'Updated Related Link "{self.object.title}" for project "{self.object.project.machine_name}"'

    def get_success_url(self) -> str:
        logger.info(
            'project.relatedlink.update.success project=%s link_id=%s link_title=%s link_url=%s',
            self.object.project.machine_name,
            self.object.id,
            self.object.title,
            self.object.uri
        )
        return reverse('sphinx_hosting:project--update', args=[self.object.project.machine_name])


class ProjectRelatedLinkDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    DeleteView
):
    model: Type[Model] = ProjectRelatedLink
    permission_required: str = 'sphinxhostingcore.change_project'

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        response = super().delete(request, *args, **kwargs)
        logger.info(
            'project.relatedlink.delete.success project=%s link_id=%s link_title=%s link_url=%s',
            self.object.project.machine_name,
            self.object.id,
            self.object.title,
            self.object.uri
        )
        return response

    def get_success_url(self) -> str:
        return reverse('sphinx_hosting:project--update', args=[self.object.project.machine_name])


# ===========================
# Versions
# ===========================


class VersionDetailView(
    LoginRequiredMixin,
    WildewidgetsMixin,
    SphinxHostingMenuMixin,
    DetailView
):
    """
    This view handles displaying the details page for a
    :py:class:`sphinx_hosting.models.Project` and handles updates to the project
    settings itself.
    """

    menu_item: str = "Projects"

    model: Type[Model] = Version
    slug_field: str = 'version'
    slug_url_kwarg: str = 'version'

    def get_object(self, queryset: QuerySet = None) -> Version:
        """
        If ``version`` is ``latest``, return the latest version of the
        :py:class:`sphinx_hosting.models.Project` whose ``machine_name`` is
        ``project_slug``.  Otherwise, return the version identified by
        ``version``.

        Raises:
            Http404: if the project has no versions, or the ``project_slug`` does
                not match any :py:class:`sphinx_hosting.models.Project` objects.

        Returns:
            The latest version of the project identified by ``project_slug``
        """
        if queryset is None:
            queryset = self.get_queryset()
        if self.kwargs['version'] == 'latest':
            project_slug = self.kwargs.get('project_slug', None)
            project = get_object_or_404(Project, machine_name=project_slug)
            version = project.latest_version
            if not version:
                raise Http404(f'Project "{project_slug}" has no versions')
            return version
        return super().get_object(queryset=queryset)

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
        """
        Generate the set of widgets for this page.

        Returns:
            A populated page layout
        """
        layout = WidgetListLayout(f'{self.object.project.title} {self.object.version}')
        layout.add_widget(VersionInfoWidget(self.object))
        layout.add_widget(VersionSphinxPageTableWidget(version_id=self.object.pk))
        layout.add_widget(VersionSphinxImageTableWidget(version_id=self.object.pk))
        if self.object.head:
            layout.add_sidebar_link_button(
                'Read Docs',
                reverse(
                    'sphinx_hosting:sphinxpage--detail',
                    args=[
                        self.object.project.machine_name,
                        self.object.version,
                        self.object.head.relative_path
                    ]
                ),
                color='primary',
                css_class='mb-3'
            )
        user = cast(AbstractUser, self.request.user)
        if user.has_perm('sphinxhostingcore.change_project'):
            layout.add_sidebar_form_button(
                'Delete Version',
                reverse('sphinx_hosting:version--delete', args=[self.object.project.machine_name, self.object.version]),
                color='outline-secondary',
                confirm_text=_("Are you sure you want to delete this version?"),
            )
        return layout

    def get_breadcrumbs(self) -> SphinxHostingBreadcrumbs:
        breadcrumbs = SphinxHostingBreadcrumbs()
        breadcrumbs.add_breadcrumb(self.object.project.title, url=self.object.project.get_absolute_url())
        breadcrumbs.add_breadcrumb(self.object.version)
        return breadcrumbs


class VersionUploadView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    FormInvalidMessageMixin,
    FormValidMessageMixin,
    BaseFormView
):
    permission_required: str = 'sphinxhostingcore.change_project'
    form_class = VersionUploadForm

    def get_form_valid_message(self) -> str:
        version = cast(Version, self.version)
        return f'Uploaded version "{version.version}" to project "{version.project.title}"'

    def form_valid(self, form: Form):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = FileSystemStorage(tmpdir)
            filename = fs.save('docs.tar.gz', content=self.request.FILES['file'])  # type: ignore
            path = os.path.join(fs.location, filename)
            self.version: Optional[Version] = None
            try:
                self.version = SphinxPackageImporter().run(filename=path, force=True)
            except Project.DoesNotExist:
                logger.error('version.upload.failed.no-such-project')
                self.messages.error(
                    'The project for the your tarball was not found.  Ensure that '
                    'the "project" field in your Sphinx "conf.py" matches the machine name '
                    'of an existing project here.'
                )
            except Exception as e:
                logger.error('version.upload.failed.unknown, error=%s', str(e))
                os.rename(path, '/tmp/uploaded_file')
                raise
        version = cast(Version, self.version)
        logger.info(
            'version.upload.success project_id=%s project_title=%s version=%s',
            version.project.id,
            version.project.title,
            version.version
        )
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse('sphinx_hosting:project--update', args=[self.kwargs['slug']])


class VersionDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    DeleteView
):
    permission_required: str = 'sphinxhostingcore.change_project'
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
        return reverse('sphinx_hosting:project--update', args=[self.kwargs['project_slug']])


# ===========================
# Pages
# ===========================

class SphinxPageDetailView(
    LoginRequiredMixin,
    WildewidgetsMixin,
    SphinxHostingMenuMixin,
    DetailView
):
    """
    This view handles displaying the actual contents of the
    :py:class:`SphinxPage`, with navigation, table of contents and the actual
    page content.
    """

    model: Type[Model] = SphinxPage
    slug_field: str = 'relative_path'
    slug_url_kwarg: str = 'path'

    def get_navbar(self) -> Navbar:
        navbar = super().get_navbar()
        globaltoc = SphinxPageGlobalTableOfContentsMenu.parse_obj(self.object.version)
        globaltoc.title = self.object.version.project.title
        navbar.add_to_menu_section(globaltoc)
        return navbar

    def get_menu_item(self) -> str:
        return self.request.path

    def get_queryset(self) -> QuerySet[SphinxPage]:
        """
        Pre-filter our default queryset so that we only are able to get
        :py:class:`sphinx_hosting.models.SphinxPage` objects associated with the
        :py:class:`sphinx_hosting.models.Version` identified by our ``project_slug``
        and ``version`` URLPath kwargs.

        If ``version`` is ``latest``, return the latest version of the
        :py:class:`sphinx_hosting.models.Project`.

        Parameters:
            project_slug: the :py:attr:`sphinx_hosting.models.Project.machine_name`
                of our project
            version: the :py:attr:`sphinx_hosting.models.Version.version` string
                of our version

        Raises:
            Http404: if ``version`` is ``latest`` and the project has no
                versions, or the ``project_slug`` does not match any
                :py:class:`sphinx_hosting.models.Project` objects.

        Returns:
            A queryset of ``SphinxPage`` objects filtered to a particular version of
            a particular project.
        """
        project_slug = self.kwargs.get('project_slug', None)
        version = self.kwargs.get('version', None)
        if version == 'latest':
            project = get_object_or_404(Project, machine_name=project_slug)
            version_obj = project.latest_version
            if not version_obj:
                raise Http404(f'Project "{project_slug}" has no versions')
            version = version_obj.version
        return super().get_queryset().filter(
            version__version=version,
            version__project__machine_name=project_slug
        )

    def get_content(self) -> Widget:
        return SphinxPageLayout(self.object)

    def get_breadcrumbs(self) -> SphinxHostingBreadcrumbs:
        """
        Return our breadcrumbs for this page::

            Home -> Project -> Version -> SphinxPage.title

        Returns:
            This page's breadcrumbs
        """
        breadcrumbs = SphinxHostingBreadcrumbs()
        breadcrumbs.add_breadcrumb(
            self.object.version.project.title,
            url=self.object.version.project.get_absolute_url()
        )
        breadcrumbs.add_breadcrumb(self.object.version.version, url=self.object.version.get_absolute_url())
        breadcrumbs.add_breadcrumb(self.object.title)
        return breadcrumbs


# ===========================
# Search Views
# ===========================

class GlobalSphinxPageSearchView(
    LoginRequiredMixin,
    MessageMixin,
    SphinxHostingMenuMixin,
    WildewidgetsMixin,
    SearchView,
):
    """
    This is the view that renders our search results.
    """
    query: Optional[str] = None
    queryset: SearchQuerySet

    def form_invalid(self, form: ModelSearchForm) -> HttpResponse:
        self.queryset = self.get_queryset()
        self.object_list = self.queryset
        self.query: str = None
        context = self.get_context_data()
        return self.render_to_response(context)

    def form_valid(self, form: ModelSearchForm) -> HttpResponse:
        self.queryset = form.search().filter(is_latest='true')
        self.facets: Dict[str, List[str]] = {}
        if project_id := self.request.GET.get('project_id', None):
            self.queryset = self.queryset.filter(project_id=project_id)
            self.facets['project_id'] = [project_id]
        if classifier_name := self.request.GET.get('classifiers', None):
            self.queryset = self.queryset.filter(classifiers=classifier_name)
            self.facets['classifiers'] = [classifier_name]
        self.object_list = self.queryset
        self.query = form.cleaned_data[self.search_field]
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_content(self) -> Widget:
        return PagedSearchLayout(self.object_list, self.query, facets=self.facets)

    def get_breadcrumbs(self) -> SphinxHostingBreadcrumbs:
        """
        Return our breadcrumbs for this page::

            Home -> Project -> Version -> SphinxPage.title

        Returns:
            This page's breadcrumbs
        """
        breadcrumbs = SphinxHostingBreadcrumbs()
        breadcrumbs.add_breadcrumb('Search')
        breadcrumbs.add_breadcrumb(f'Query: "{self.query}"')
        return breadcrumbs
