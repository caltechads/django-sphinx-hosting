from typing import Dict, List, Type

from django.db.models import Model, QuerySet
from wildewidgets import (
    BasicModelTable,
    CrispyFormModalWidget,
    CrispyFormWidget,
    CardWidget,
    Widget,
    WidgetListLayoutHeader,
)

from .core import Datagrid

from ..forms import ProjectCreateForm
from ..models import Project, Version


#------------------------------------------------------
# Modals
#------------------------------------------------------

class ProjectCreateModalWidget(CrispyFormModalWidget):
    """
    This is a modal dialog that holds the
    :py:class:`sphinx_hosting.forms.ProjectCreateForm`.
    """

    modal_id: str = "project__create"
    modal_title: str = "Add Project"

    def __init__(self, *args, **kwargs):
        form = ProjectCreateForm()
        super().__init__(form=form, *args, **kwargs)


#------------------------------------------------------
# Project related widgets
#------------------------------------------------------

class ProjectInfoWidget(CardWidget):
    """
    This is a :py:class:`wildewidgets.CardWidget` containing a Tabler datagrid
    that gives information about a :py:class:`sphinx_hosting.models.Project`.
    """

    title: str = "Project Info"
    icon: str = "info-square"

    def __init__(self, project: Project, **kwargs):
        super().__init__(**kwargs)
        grid = Datagrid()
        grid.add_item(title='Machine Name', content=project.machine_name)
        grid.add_item(title='Created', content=project.created.strftime('%Y-%m-%d %H:%M %Z'))
        grid.add_item(title='Last Modified', content=project.modified.strftime('%Y-%m-%d %H:%M %Z'))
        self.set_widget(grid)


class ProjectTableWidget(CardWidget):
    """
    This is a :py:class:`wildewidgets.CardWidget` that gives our
    :py:class:`ProjectTable` dataTable a nice header with a total book count and
    an "Add Project" button that opens a modal dialog.
    """
    title: str = "Projects"
    icon: str = "window"

    def __init__(self, **kwargs):
        super().__init__(widget=ProjectTable(), **kwargs)

    def get_title(self) -> WidgetListLayoutHeader:
        header = WidgetListLayoutHeader(
            header_text="Projects",
            badge_text=Project.objects.count(),
        )
        header.add_modal_button(
            text="New Project",
            color="primary",
            target=f'#{ProjectCreateModalWidget.modal_id}'
        )
        return header


class ProjectVersionsTableWidget(CardWidget):
    """
    This is a :py:class:`wildewidgets.CardWidget` that gives our
    :py:class:`ProjectVersionTable` dataTable a nice header with a total version
    count.
    """
    title: str = "Versions"
    icon: str = "bookmark-star"

    def __init__(self, project_id: int, **kwargs):
        self.project_id = project_id
        super().__init__(
            widget=ProjectVersionTable(project_id=project_id),
            **kwargs,
        )

    def get_title(self) -> WidgetListLayoutHeader:
        header = WidgetListLayoutHeader(
            header_text="Versions",
            badge_text=Project.objects.get(pk=self.project_id).versions.count(),
        )
        return header


class ProjectDetailWidget(
    CrispyFormWidget,
    Widget
):
    """
    This widget renders an update form for a :py:class:`sphinx_hosting.models.Project`.

    Use directly it like so::

        >>> project = Project.objects.get(pk=1)
        >>> form = ProjectUpdateForm(instance=project)
        >>> widget = ProjectDetailWidget(form=form)

    Or you can simply add the form to your view context and
    :py:class:`ProjectDetailWidget` will pick it up automatically.
    """
    title: str = "General Settings"
    name: str = 'project-detail__section'
    modifier: str = 'general'
    icon: str = "card-checklist"
    css_class: str = CrispyFormWidget.css_class + " p-4"


#------------------------------------------------------
# Datatables
#------------------------------------------------------

class ProjectTable(BasicModelTable):
    """
    This widget displays a `dataTable <https://datatables.net>`_ of our
    :py:class:`sphinx_hosting.models.Project` instances.

    It's used as a the main widget in by :py:class:`ProjectTableWidget`.
    """

    model: Type[Model] = Project

    #: Show this many rows per page
    page_length: int = 25
    #: Set to ``True`` to stripe our table rows
    striped: bool = True
    actions: bool = True
    #: A list of fields that we will list as columns.  These are either fields
    #: on our :py:attr:`model`, or defined as ``render_FIELD_NAME_column`` methods
    #: on this class
    fields: List[str] = [
        'title',
        'machine_name',
        'latest_version',
        'latest_version_date',
    ]
    #: A list of names of columns to hide by default.
    hidden: List[str] = [
        'machine_name'
    ]
    #: A list of names of columns that will will not be searched when doing a
    #: **global** search
    unsearchable: List[str] = [
        'lastest_version',
        'latest_version_date',
    ]
    #: A dict of column name to column label.  We use it to override the
    #: default labels for the named columns
    verbose_names: Dict[str, str] = {
        'title': 'Project Name',
        'machine_name': 'Machine Name',
        'latest_version': 'Latest Version',
        'latest_version_date': 'Import Date',
    }
    #: A dict of column names to alignment ("left", "right", "center")
    alignment: Dict[str, str] = {
        'title': 'left',
        'machine_name': 'left',
        'latest_version': 'left',
        'latest_version_date': 'left'
    }

    def render_latest_version_column(self, row: Project, column: str) -> str:
        """
        Render our ``latest_version`` column.  This is the version string of the
        :py:class:`sphinx_hosting.models.Version` that has the most recent
        :py:attr:`sphinx_hosting.models.Version.modified` timestamp.

        If there are not yet any :py:class:`sphinx_hosting.models.Version` instances for
        this project, return empty string.

        Args:
            row: the ``Project`` we are rendering
            colunn: the name of the column to render

        Returns:
            The version string of the most recently published version, or empty
            string.
        """
        version = row.versions.order_by('-modified').first()
        if version:
            return version.version
        return ''

    def render_latest_version_date_column(self, row: Project, column: str) -> str:
        """
        Render our ``latest_version_date`` column.  This is the last modified
        date of the :py:class:`sphinx_hosting.models.Version` that has the most
        recent :py:attr:`sphinx_hosting.models.Version.modified` timestamp.

        If there are not yet any :py:class:`sphinx_hosting.models.Version` instances for
        this project, return empty string.

        Args:
            row: the ``Project`` we are rendering
            colunn: the name of the column to render

        Returns:
            The of the most recently published version, or empty
            string.
        """
        version = row.versions.order_by('-modified').first()
        if version:
            return self.render_datetime_type_column(version.modified)
        return ''


class ProjectVersionTable(BasicModelTable):
    """
    This widget displays a `dataTable <https://datatables.net>`_ of our
    :py:class:`sphinx_hosting.models.Version` instances for a particular
    :py:class:`sphinx_hosting.models.Project`.

    It's used as a the main widget in by :py:class:`ProjectVersionTableWidget`.
    """

    model: Type[Model] = Version

    #: Show this many rows per page
    page_length: int = 25
    #: Set to ``True`` to stripe our table rows
    striped: bool = True
    actions: bool = True

    #: A list of fields that we will list as columns.  These are either fields
    #: on our :py:attr:`model`, or defined as ``render_FIELD_NAME_column`` methods
    #: on this class
    fields: List[str] = [
        'version',
        'num_pages',
        'num_images',
        'created',
        'modified',
    ]
    #: A list of names of columns that will will not be searched when doing a
    #: **global** search
    unsearchable: List[str] = [
        'num_pages',
        'num_images',
    ]
    #: A dict of column name to column label.  We use it to override the
    #: default labels for the named columns
    verbose_names: Dict[str, str] = {
        'title': 'Version',
        'num_pages': '# Pages',
        'num_images': '# Images',
    }
    #: A dict of column names to alignment ("left", "right", "center")
    alignment: Dict[str, str] = {
        'version': 'center',
        'num_pages': 'right',
        'num_images': 'right',
        'created': 'left',
        'modified': 'left'
    }

    def __init__(self, *args,  **kwargs):
        """
        One of our ``kwargs`` must be ``project_id``, the ``pk`` of the
        :py:class:`sphinx_hosting.models.Project` for which we want to list
        :py:class:`sphinx_hosting.models.Version` objects.

        This will get added to the :py:attr:`extra_data` dict in the ``kwargs``
        key, from which we reference it.
        """
        #: The pk of the :py:class:`sphinx_hosting.models.Project` for which to list versions
        self.project_id: int = None
        super().__init__(self, *args, **kwargs)
        if 'project_id' in self.extra_data['kwargs']:
            self.project_id = int(self.extra_data['kwargs']['project_id'])

    def get_initial_queryset(self) -> QuerySet[Version]:
        """
        Filter our :py:class:`sphinx_hosting.models.Version` objects by
        :py:attr:`project_id`.

        Returns:
            A filtered :py:class:`QuerySet` on :py:class:`sphinx_hosting.models.Version`
        """
        qs = super().get_initial_queryset().filter(project_id=self.project_id)
        return qs.order_by('-version')

    def render_num_pages_column(self, row: Version, column: str) -> str:
        """
        Render our ``num_pages`` column.  This is the number of
        :py:class:`sphinx_hosting.models.SphinxPage` objects imported for this
        version.

        Args:
            row: the ``Version`` we are rendering
            colunn: the name of the column to render

        Returns:
            The number of pages for this version.
        """
        return row.pages.count()

    def render_num_images_column(self, row: Version, column: str) -> str:
        """
        Render our ``num_images`` column.  This is the number of
        :py:class:`sphinx_hosting.models.SphinxImage` objects imported for this
        version.

        Args:
            row: the ``Version`` we are rendering
            colunn: the name of the column to render

        Returns:
            The number of images for this version.
        """
        return row.images.count()
