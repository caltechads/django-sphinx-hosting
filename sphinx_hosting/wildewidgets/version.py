from typing import Dict, List, Type

from django.db.models import Model, QuerySet
from django.db.models.functions import Length
from wildewidgets import (
    BasicModelTable,
    CardWidget,
    Datagrid,
    WidgetListLayoutHeader
)

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
            content=version.project.title,
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

