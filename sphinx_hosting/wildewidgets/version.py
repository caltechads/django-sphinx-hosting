from typing import Dict, List, Type

from django.db.models import Model, QuerySet
from django.db.models.functions import Length
from wildewidgets import (
    BasicModelTable,
    CardWidget,
    WidgetListLayoutHeader
)

from .core import Datagrid
from ..models import (
    Project,
    SphinxImage,
    SphinxPage,
    Version
)


class VersionInfoWidget(CardWidget):

    title: str = "Version Info"
    icon: str = "info-square"

    def __init__(self, version: Project, **kwargs):
        super().__init__(**kwargs)
        grid = Datagrid()
        grid.add_item(
            title='Project',
            content=version.project.machine_name,
            url=version.project.get_absolute_url()
        )
        grid.add_item(title='Version Created', content=version.created.strftime('%Y-%m-%d %H:%M %Z'))
        grid.add_item(title='Version Last Modified', content=version.modified.strftime('%Y-%m-%d %H:%M %Z'))
        grid.add_item(title='Sphinx Version', content=version.sphinx_version)
        self.set_widget(grid)


class VersionSphinxPageTableWidget(CardWidget):
    """
    This is a :py:class:`wildewidgets.CardWidget` that gives our
    :py:class:`VersionSphinxPageTable` dataTable a nice header with a total
    page count.
    """
    title: str = "Pages"
    icon: str = "bookmark-star"

    def __init__(self, version_id: int, **kwargs):
        self.version_id = version_id
        super().__init__(
            widget=VersionSphinxPageTable(version_id=version_id),
            **kwargs,
        )

    def get_title(self) -> WidgetListLayoutHeader:
        header = WidgetListLayoutHeader(
            header_text="Pages",
            badge_text=Version.objects.get(pk=self.version_id).pages.count(),
        )
        return header


class VersionSphinxImageTableWidget(CardWidget):
    """
    This is a :py:class:`wildewidgets.CardWidget` that gives our
    :py:class:`VersionSphinxImageTable` dataTable a nice header with a total
    image count.
    """
    title: str = "Images"
    icon: str = "bookmark-star"

    def __init__(self, version_id: int, **kwargs):
        self.version_id = version_id
        super().__init__(
            widget=VersionSphinxImageTable(version_id=version_id),
            **kwargs,
        )

    def get_title(self) -> WidgetListLayoutHeader:
        header = WidgetListLayoutHeader(
            header_text="Images",
            badge_text=Version.objects.get(pk=self.version_id).images.count(),
        )
        return header


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

    page_length: int = 25  #: Show this many books per page
    striped: bool = True   #: Set to ``True`` to stripe our table rows
    actions: bool = True

    fields: List[str] = [  #: These are the fields on our model (or which are computed) that we will list as columns
        'title',
        'machine_name',
        'latest_version',
        'latest_version_date',
    ]
    hidden: List[str] = [  #: the columns that start as hidden
        'machine_name'
    ]
    unsearchable: List[str] = [  #: These columns will not be searched when doing a **global** search
        'lastest_version',
        'latest_version_date',
    ]
    verbose_names: Dict[str, str] = {  #: Override the default labels labels for the named columns
        'title': 'Project Name',
        'machine_name': 'Machine Name',
        'latest_version': 'Latest Version',
        'latest_version_date': 'Import Date',
    }
    alignment: Dict[str, str] = {  #: declare how we horizontally align our columns
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

    page_length: int = 25  #: Show this many books per page
    striped: bool = True   #: Set to ``True`` to stripe our table rows
    actions: bool = True

    fields: List[str] = [  #: These are the fields on our model (or which are computed) that we will list as columns
        'version',
        'num_pages',
        'num_images',
        'created',
        'modified',
    ]
    unsearchable: List[str] = [  #: These columns will not be searched when doing a **global** search
        'num_pages',
        'num_images',
    ]
    verbose_names: Dict[str, str] = {  #: Override the default labels labels for the named columns
        'title': 'Version',
        'num_pages': '# Pages',
        'num_images': '# Images',
    }
    alignment: Dict[str, str] = {  #: declare how we horizontally align our columns
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


class VersionSphinxPageTable(BasicModelTable):
    """
    This widget displays a `dataTable <https://datatables.net>`_ of our
    :py:class:`sphinx_hosting.models.SphinxPage` instances for a particular
    :py:class:`sphinx_hosting.models.Version`.

    It's used as a the main widget in by :py:class:`VersionSphinxPageTableWidget`.
    """

    model: Type[Model] = SphinxPage

    page_length: int = 25  #: Show this many books per page
    striped: bool = True   #: Set to ``True`` to stripe our table rows
    actions: bool = True

    fields: List[str] = [  #: These are the fields on our model (or which are computed) that we will list as columns
        'title',
        'relative_path',
        'size',
    ]
    alignment: Dict[str, str] = {  #: declare how we horizontally align our columns
        'title': 'left',
        'relative_path': 'left',
        'size': 'right',
    }

    def __init__(self, *args,  **kwargs):
        """
        One of our ``kwargs`` must be ``version_id``, the ``pk`` of the
        :py:class:`sphinx_hosting.models.Version` for which we want to list
        :py:class:`sphinx_hosting.models.SphinxPage` objects.

        This will get added to the :py:attr:`extra_data` dict in the ``kwargs``
        key, from which we reference it.
        """
        self.version_id: int = None  #: The pk of the :py:class:`sphinx_hosting.models.Version` for which to list pages
        super().__init__(self, *args, **kwargs)
        if 'version_id' in self.extra_data['kwargs']:
            self.version_id = int(self.extra_data['kwargs']['version_id'])

    def get_initial_queryset(self) -> QuerySet[SphinxPage]:
        """
        Filter our :py:class:`sphinx_hosting.models.SphinxPage` objects by
        :py:attr:`version_id`.
        """
        qs = (
            super().get_initial_queryset()
            .filter(version_id=self.version_id)
            .annotate(size=Length('body'))
        )
        return qs.order_by('title')


class VersionSphinxImageTable(BasicModelTable):
    """
    This widget displays a `dataTable <https://datatables.net>`_ of our
    :py:class:`sphinx_hosting.models.SphinxImage` instances for a particular
    :py:class:`sphinx_hosting.models.Version`.

    It's used as a the main widget in by :py:class:`VersionSphinxImageTableWidget`.
    """

    model: Type[Model] = SphinxImage

    page_length: int = 25  #: Show this many books per page
    striped: bool = True   #: Set to ``True`` to stripe our table rows

    fields: List[str] = [  #: These are the fields on our model (or which are computed) that we will list as columns
        'orig_path',
        'file_path',
        'size',
    ]
    alignment: Dict[str, str] = {  #: declare how we horizontally align our columns
        'orig_path': 'left',
        'file_path': 'left',
        'size': 'right',
    }

    def __init__(self, *args,  **kwargs):
        """
        One of our ``kwargs`` must be ``version_id``, the ``pk`` of the
        :py:class:`sphinx_hosting.models.Version` for which we want to list
        :py:class:`sphinx_hosting.models.SphinxPage` objects.

        This will get added to the :py:attr:`extra_data` dict in the ``kwargs``
        key, from which we reference it.
        """
        self.version_id: int = None  #: The pk of the :py:class:`sphinx_hosting.models.Version` for which to list pages
        super().__init__(self, *args, **kwargs)
        if 'version_id' in self.extra_data['kwargs']:
            self.version_id = int(self.extra_data['kwargs']['version_id'])

    def get_initial_queryset(self) -> QuerySet[SphinxPage]:
        """
        Filter our :py:class:`sphinx_hosting.models.SphinxPage` objects by
        :py:attr:`version_id`.
        """
        qs = (
            super().get_initial_queryset()
            .filter(version_id=self.version_id)
        )
        return qs.order_by('orig_path')

    def render_size_column(self, row: Version, column: str) -> str:
        """
        Render our ``size`` column.  This is the size in bytes of the
        :py:attr:`sphinx_hosting.models.SphinxImage.file` field.

        Args:
            row: the ``Version`` we are rendering
            colunn: the name of the column to render

        Returns:
            The size in bytes of the uploaded file.
        """
        return str(row.file.size)

    def render_file_path_column(self, row: Version, column: str) -> str:
        """
        Render our ``file_path`` column.  This is the path to the file in
        ``MEDIA_ROOT``.

        Args:
            row: the ``Version`` we are rendering
            colunn: the name of the column to render

        Returns:
            The size in bytes of the uploaded file.
        """
        return str(row.file.name)

