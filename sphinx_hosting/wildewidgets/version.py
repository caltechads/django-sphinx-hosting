from typing import Dict, Final, List, Optional, Type  # noqa: UP035

from django.db.models import Model, QuerySet
from django.db.models.functions import Length
from wildewidgets import (
    BasicModelTable,
    Block,
    CardWidget,
    CrispyFormWidget,
    Datagrid,
    WidgetListLayoutHeader,
)

from ..models import SphinxDocument, SphinxImage, SphinxPage, Version


class VersionInfoWidget(CardWidget):
    """
    Gives a :py:class:`wildewidget.Datagrid` type overview of
    information about this version:

    * A link to the project that owns this
      :py:class:`sphinx_hosting.models.Version`
    * Create and last modified timestamps
    * What version of Sphinx was used to generate the pages

    Args:
        version: the ``Version`` object we're describing

    """

    title: str = "Version Info"
    icon: str = "info-square"

    def __init__(self, version: Version, **kwargs):
        super().__init__(**kwargs)
        grid = Datagrid()
        grid.add_item(
            title="Project",
            content=version.project.title,  # type: ignore[attr-defined]
            url=version.project.get_absolute_url(),  # type: ignore[attr-defined]
        )
        grid.add_item(
            title="Version Created",
            content=version.created.strftime("%Y-%m-%d %H:%M %Z"),
        )
        grid.add_item(
            title="Version Last Modified",
            content=version.modified.strftime("%Y-%m-%d %H:%M %Z"),
        )
        grid.add_item(title="Sphinx Version", content=version.sphinx_version)
        self.set_widget(grid)


class VersionSphinxPageTableWidget(CardWidget):
    """
    A :py:class:`wildewidgets.CardWidget` that gives our
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
        return WidgetListLayoutHeader(
            header_text="Pages",
            badge_text=Version.objects.get(pk=self.version_id).pages.count(),
        )


class VersionUploadBlock(CardWidget):
    """
    Holds the upload form for uploading documentation tarballs.  Once
    uploaded, the tarball will be run through
    :py:class:`sphinx_hosting.importers.SphinxPackageImporter` to actually
    import it into the database.
    """

    css_class: str = "my-3 border"

    def __init__(self, *blocks, form=None, **kwargs):  # noqa: ARG002
        super().__init__(
            widget=CrispyFormWidget(form=form, name="project__upload_docs"), **kwargs
        )
        self.set_header(Block("Import Docs", tag="h3"))


class VersionSphinxImageTableWidget(CardWidget):
    """
    A :py:class:`wildewidgets.CardWidget` that gives our
    :py:class:`VersionSphinxImageTable` dataTable a nice header with a total
    image count.
    """

    title: str = "Images"
    icon: str = "images"

    def __init__(self, version_id: int, **kwargs):
        self.version_id = version_id
        super().__init__(
            widget=VersionSphinxImageTable(version_id=version_id),
            **kwargs,
        )

    def get_title(self) -> WidgetListLayoutHeader:
        return WidgetListLayoutHeader(
            header_text="Images",
            badge_text=Version.objects.get(pk=self.version_id).images.count(),
        )


class VersionSphinxDocumentTableWidget(CardWidget):
    """
    A :py:class:`wildewidgets.CardWidget` that gives our
    :py:class:`VersionSphinxDocumentTable` dataTable a nice header with a total
    image count.
    """

    title: str = "Documents"
    icon: str = "files"

    def __init__(self, version_id: int, **kwargs):
        self.version_id = version_id
        super().__init__(
            widget=VersionSphinxDocumentTable(version_id=version_id),
            **kwargs,
        )

    def get_title(self) -> WidgetListLayoutHeader:
        return WidgetListLayoutHeader(
            header_text="Documents",
            badge_text=Version.objects.get(pk=self.version_id).documents.count(),
        )


# ------------------------------------------------------
# Datatables
# ------------------------------------------------------


class VersionSphinxPageTable(BasicModelTable):
    """
    Displays a `dataTable <https://datatables.net>`_ of our
    :py:class:`sphinx_hosting.models.SphinxPage` instances for a particular
    :py:class:`sphinx_hosting.models.Version`.

    It's used as a the main widget in by :py:class:`VersionSphinxPageTableWidget`.
    """

    model: Type[Model] = SphinxPage
    #: Show this many books per page
    page_length: int = 25
    #: Set to ``True`` to stripe our table rows
    striped: bool = True
    actions: bool = True

    #: These are the fields on our model (or which are computed) that we will
    #: list as columns
    fields: Final[List[str]] = [
        "title",
        "relative_path",
        "size",
    ]
    #: Declare how we horizontally align our columns
    alignment: Final[Dict[str, str]] = {
        "title": "left",
        "relative_path": "left",
        "size": "right",
    }

    def __init__(self, *args, **kwargs) -> None:
        """
        One of our ``kwargs`` must be ``version_id``, the ``pk`` of the
        :py:class:`sphinx_hosting.models.Version` for which we want to list
        :py:class:`sphinx_hosting.models.SphinxPage` objects.

        This will get added to the :py:attr:`extra_data` dict in the ``kwargs``
        key, from which we reference it.
        """
        #: The pk of the :py:class:`sphinx_hosting.models.Version` for which to
        #: list pages
        self.version_id: Optional[int] = kwargs.get("version_id", None)  # noqa: FA100
        super().__init__(*args, **kwargs)
        if "version_id" in self.extra_data["kwargs"]:
            self.version_id = int(self.extra_data["kwargs"]["version_id"])

    def get_initial_queryset(self) -> QuerySet[SphinxPage]:
        """
        Filter our :py:class:`sphinx_hosting.models.SphinxPage` objects by
        :py:attr:`version_id`.
        """
        qs = (
            super()
            .get_initial_queryset()
            .filter(version_id=self.version_id)
            .annotate(size=Length("body"))
        )
        return qs.order_by("title")


class VersionSphinxImageTable(BasicModelTable):
    """
    Displays a `dataTable <https://datatables.net>`_ of our
    :py:class:`sphinx_hosting.models.SphinxImage` instances for a particular
    :py:class:`sphinx_hosting.models.Version`.

    It's used as a the main widget in by
    :py:class:`VersionSphinxImageTableWidget`.
    """

    model: Type[Model] = SphinxImage
    #: Show this many books per page
    page_length: int = 25
    #: Set to ``True`` to stripe our table rows
    striped: bool = True

    #: These are the fields on our model (or which are computed) that we will
    #: list as columns
    fields: Final[List[str]] = [
        "orig_path",
        "file_path",
        "size",
    ]
    #: Declare how we horizontally align our columns
    alignment: Final[Dict[str, str]] = {
        "orig_path": "left",
        "file_path": "left",
        "size": "right",
    }

    def __init__(self, *args, **kwargs) -> None:
        """
        One of our ``kwargs`` must be ``version_id``, the ``pk`` of the
        :py:class:`sphinx_hosting.models.Version` for which we want to list
        :py:class:`sphinx_hosting.models.SphinxPage` objects.

        This will get added to the :py:attr:`extra_data` dict in the ``kwargs``
        key, from which we reference it.
        """
        #: The pk of the :py:class:`sphinx_hosting.models.Version` for which to
        #: list pages
        self.version_id: Optional[int] = kwargs.get("version_id", None)  # noqa: FA100
        super().__init__(*args, **kwargs)
        if "version_id" in self.extra_data["kwargs"]:
            self.version_id = int(self.extra_data["kwargs"]["version_id"])

    def get_initial_queryset(self) -> QuerySet[SphinxPage]:
        """
        Filter our :py:class:`sphinx_hosting.models.SphinxPage` objects by
        :py:attr:`version_id`.
        """
        qs = super().get_initial_queryset().filter(version_id=self.version_id)
        return qs.order_by("orig_path")

    def render_size_column(self, row: Version, _: str) -> str:
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

    def render_file_path_column(self, row: Version, _: str) -> str:
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


class VersionSphinxDocumentTable(BasicModelTable):
    """
    Displays a `dataTable <https://datatables.net>`_ of our
    :py:class:`sphinx_hosting.models.SphinxDocument` instances for a particular
    :py:class:`sphinx_hosting.models.Version`.

    It's used as a the main widget in by
    :py:class:`VersionSphinxDocumentTableWidget`.
    """

    model: Type[Model] = SphinxDocument
    #: Show this many books per page
    page_length: int = 25
    #: Set to ``True`` to stripe our table rows
    striped: bool = True

    #: These are the fields on our model (or which are computed) that we will
    #: list as columns
    fields: Final[List[str]] = [
        "orig_path",
        "file_path",
        "size",
    ]
    #: Declare how we horizontally align our columns
    alignment: Final[Dict[str, str]] = {
        "orig_path": "left",
        "file_path": "left",
        "size": "right",
    }

    def __init__(self, *args, **kwargs) -> None:
        """
        One of our ``kwargs`` must be ``version_id``, the ``pk`` of the
        :py:class:`sphinx_hosting.models.Version` for which we want to list
        :py:class:`sphinx_hosting.models.SphinxPage` objects.

        This will get added to the :py:attr:`extra_data` dict in the ``kwargs``
        key, from which we reference it.
        """
        #: The pk of the :py:class:`sphinx_hosting.models.Version` for which to
        #: list pages
        self.version_id: Optional[int] = kwargs.get("version_id", None)  # noqa: FA100
        super().__init__(*args, **kwargs)
        if "version_id" in self.extra_data["kwargs"]:
            self.version_id = int(self.extra_data["kwargs"]["version_id"])

    def get_initial_queryset(self) -> QuerySet[SphinxPage]:
        """
        Filter our :py:class:`sphinx_hosting.models.SphinxPage` objects by
        :py:attr:`version_id`.
        """
        qs = super().get_initial_queryset().filter(version_id=self.version_id)
        return qs.order_by("orig_path")

    def render_size_column(self, row: Version, _: str) -> str:
        """
        Render our ``size`` column.  This is the size in bytes of the
        :py:attr:`sphinx_hosting.models.SphinxDocument.file` field.

        Args:
            row: the ``Version`` we are rendering
            colunn: the name of the column to render

        Returns:
            The size in bytes of the uploaded file.

        """
        return str(row.file.size)

    def render_file_path_column(self, row: Version, _: str) -> str:
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
