from copy import copy
from functools import partial
import re
from typing import Any, Dict, List, Optional, Tuple, Type, Union

from django.core.exceptions import ImproperlyConfigured
from django.db.models import Model, QuerySet
from django.db.models.functions import Length
from django.templatetags.static import static
from django.urls import reverse
from wildewidgets import (
    BasicModelTable,
    Block,
    BreadrumbBlock,
    CardHeader,
    CardWidget,
    CrispyFormWidget,
    CrispyFormModalWidget,
    HTMLWidget,
    LinkButton,
    VerticalDarkMenu,
    Widget,
    WidgetListLayoutHeader,
)

from .forms import ProjectCreateForm
from .models import Project, SphinxImage, SphinxPage, Version

MenuItem = Union[Tuple[str, str], Tuple[str, str, Dict[str, str]]]
DatagridItemDef = Union["DatagridItem", Tuple[str, str], Tuple[str, str, Dict[str, Any]]]
ColumnSet = Union[List["Column"], Dict[str, "Column"]]


#------------------------------------------------------
# Widgets
#------------------------------------------------------

class DatagridItem(Block):
    """
    This widget implements a `Tabler datagrid-item
    <https://preview.tabler.io/docs/datagrid.html`_ It should be used with
    :py:class:`Datagrid`.

    Args:
        title: the ``datagrid-title`` of the ``datagrid-item``
        content: the ``datagrid-content`` of the ``datagrid-item``
        link: URL to use to turn content into a hyperlink
    """
    block: str = 'datagrid-item'
    title: Optional[str] = None  #: the ``datagrid-title`` of the ``datagrid-item``
    content: Optional[str] = None  #: the ``datagrid-content`` of the ``datagrid-item``
    link: Optional[str] = None  #: a URL to use to turn content into a hyperlink

    def __init__(self, **kwargs):
        self.title = kwargs.pop('title', self.title)
        self.content = kwargs.pop('content', self.content)
        self.link = kwargs.pop('link', self.link)
        super().__init__(**kwargs)
        if self.link:
            content: Block = Block(
                self.content,
                tag='a',
                attributes={'href': self.link},
                name='datagrid-conetnt'
            )
        else:
            content: Block = Block(self.content, name='datagrid-conetnt')
        self.add_block(Block(self.title, name='datagrid-title'))
        self.add_block(content)


class Datagrid(Block):
    """
    This widget implements a `Tabler Data grid <https://preview.tabler.io/docs/datagrid.html`_
    To use it, create :py:class:`DatagridItem`.
    It should be used with :py:class:`DatagridItem`.

    Keyword Args:
        items: a list of ``datagrid-items`` to add to our content
    """
    block: str = 'datagrid'
    items: List[DatagridItemDef] = []  #: a list of ``datagrid-items`` to add to our content

    def __init__(self, **kwargs):
        items = kwargs.pop('items', self.__class__.items)
        super().__init__(**kwargs)
        for item in items:
            if isinstance(item, DatagridItem):
                self.add_block(item)
            elif isinstance(item, tuple):
                if len(item) == 2:
                    self.add_item(item[0], item[1])
                else:
                    self.add_item(item[0], item[1], **item[2])

    def add_item(self, title: str, content: str, link: str = None, **kwargs) -> None:
        """
        Add a :py:class:`DatagridItem` to our block contents, with
        ``datagrid-title`` of ``title`` and datagrid

        Keyword Args:
            title: the ``datagrid-title`` of the ``datagrid-item``
            content: the ``datagrid-content`` of the ``datagrid-item``
            link: URL to use to turn content into a hyperlink
        """
        self.add_block(DatagridItem(title=title, content=content, link=link, **kwargs))


class Column(Block):

    block: str = 'column'
    width: Optional[int] = None  #: a column width between 0 and 12
    alignment: Optional[str] = None

    def __init__(self, *args, **kwargs):
        self.width: int = kwargs.pop('width', self.__class__.width)
        self.alignment: str = kwargs.pop('alignment', self.__class__.alignment)
        super().__init__(*args, **kwargs)
        col = ' col'
        if self.width:
            if self.width < 1 or self.width > 12:
                raise ImproperlyConfigured('If specified, column width must be in the range [1, 12]')
            col = f' col-{self.width}'
        if self._css_class is None:
            self._css_class = ''
        self._css_class += col
        if self.alignment:
            self._css_class += f' d-flex flex-column align-items-{self.alignment}'


class Row(Block):

    block: str = 'row'
    columns: List[Column] = []

    def __init__(self, **kwargs):
        columns = kwargs.pop('columns', copy(self.__class__.columns))
        self.columns: List[Column] = columns
        self.columns_map: Dict[str, Column] = {}
        for i, column in enumerate(self.columns):
            if column._name:
                name = column._name
            else:
                name = f'column-{i+1}'
            self.columns_map[name] = column
            self._add_helper_method(name)
        super().__init__(**kwargs)

    @property
    def column_names(self) -> List[str]:
        """
        Return the list of names of all of our columns.

        Returns:
            A list of column names.
        """
        return list(self.columns_map.keys())

    def _add_helper_method(self, name: str) -> None:
        """
        Add a method to this :py:class:`Row` object like so:

            def add_to_column_name(widget: Widget) -> None:
                ...

        This new method will allow you to add a widget to the
        column with name ``name`` directly without having to use
        :py:meth:`add_to_column`.

        Example:

            > sidebar = Column(name='sidebar', width=3)
            > main = Column(name='main')
            > row = Row(columns=[sidebar, main])

            You can now add widgets to the sidebar column like so:

            > widget = Block('foo')
            > row.add_to_sidebar(widget)

        Args:
            name: the name of the column
        """
        name = re.sub('-', '_', name)
        setattr(self, f'add_to_{name}', partial(self.add_to_column, name))

    def add_column(self, column: Column) -> None:
        """
        Add a column to this row to the right of any existing columns.

        Note:
            A side effect of adding a column is to add a method to this
            :py:class:`Row` object like so::

                def add_to_column_name(widget: Widget) -> None:

            where ``column_name`` is either:

            * the value of ``column.name``, if that is not the default name

        Args:
            column: the column to add
        """
        if column._name:
            name: str = column._name
        else:
            name = f'column-{len(self.columns)}'
        self.add_block(column)
        self.columns.append(column)
        self.columns_map[name] = column
        self._add_helper_method(name)

    def add_to_column(self, identifier: Union[int, str], widget: Widget) -> None:
        """
        Add ``widget`` to the column named ``identifier`` at the bottom of any
        other widgets in that column.

        Note:
            If ``identifier`` is an int, ``identifier`` should be 1-offset, not
            0-offset.

        Args:
            identifier: either a column number (left to right, starting with 1),
                or a column name
            widget: the widget to append to this col
        """
        if isinstance(identifier, int):
            identifier = f'column-{identifier}'
        self.columns_map[identifier].add_block(widget)


class FontIcon(Block):
    """
    Render a font-based Bootstrap icon, for example::

        <i class="bi-star"></i>

    See the `Boostrap Icons <https://icons.getbootstrap.com/>`_ list for the
    list of icons.  Find an icon you like, and use the name of that icon on that
    page as the ``icon`` kwarg to the constructor, or set it as the :py:attr:`icon`
    class variable.

        icon: If set, use this as the name for the icon to render
        color: If set, use this as Tabler color name to use as the foreground
            font color.  If :py:at
        bac: If set, use this as Tabler color name to use as the foreground
            font color


    Keyword Args:
        icon: the name of the icon to render
    """

    tag = 'i'
    prefix: str = 'bi'
    #: If not ``None``, use this as the name for the icon to render
    icon: Optional[str] = None
    #: If not ``None``, use this as Tabler color name to use as the foreground
    #: font color.  If :py:attr:`background` is also set, this is ignored.  Look
    #: at `Tabler: Colors <https://preview.tabler.io/docs/colors.html>`_
    #: for your choices; set this to the text after the ``bg-``
    color: Optional[str] = None
    #: If not ``None``, use this as Tabler background/foreground color set for
    #: this icon.  : This overrides :py:attr:`color`. Look
    #: at `Tabler: Colors <https://preview.tabler.io/docs/colors.html>`_
    #: for your choices; set this to the text after the ``bg-``
    background: Optional[str] = None

    def __init__(
        self,
        icon: Optional[str] = None,
        color: Optional[str] = None,
        background: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.color = color if color else self.__class__.color
        self.background = background if background else self.__class__.background
        self.icon = f'{self.prefix}-{icon}'
        if self._css_class is None:
            self._css_class = ''
        self._css_class += f' {self.icon}'
        if self.color:
            self._css_class += f' text-{self.color} bg-transparent'
        elif self.background:
            self._css_class += f' bg-{self.background} text-{self.background}-fg'


class TwoColumnLayoutWidget(Row):

    name: str = 'two-column'
    left_column_width: Optional[int] = None
    left_column_widgets: List[Widget] = []
    right_column_widgets: List[Widget] = []

    def __init__(self, **kwargs):
        left_column_width = kwargs.pop('left_column_width', self.__class__.left_column_width)
        super().__init__(**kwargs)
        self.add_column(Column(
            *kwargs.pop('left_column_widgets', self.left_column_widgets),
            name='left',
            width=left_column_width
        ))
        self.add_column(Column(
            *kwargs.pop('right_column_widgets', self.right_column_widgets),
            name='right',
        ))


#------------------------------------------------------
# Navigation
#------------------------------------------------------

class SphinxHostingMenu(VerticalDarkMenu):
    """
    A main menu for all ``sphinx_hosting`` views.   To use it, subclass this and:

    * Add your own menu items it :py:attr:`items`
    * Change the menu logo by updating :py:attr:`brand_image`
    * Change the menu logo alt text by updating :py:attr:`brand_text`
    """

    brand_image: str = static("sphinx_hosting/images/logo.jpg")
    brand_image_width: str = '100%'
    brand_text: str = "Sphinx Hosting"
    items: List[Tuple[str, str]] = [
        ('Projects', 'sphinx_hosting:project--list'),
    ]


class SphinxHostingBreadcrumbs(BreadrumbBlock):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_breadcrumb('Sphinx Hosting', reverse('sphinx_hosting:project--list'))


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
    This is a :py:class:`wildewidgets.CardWidget` that gives our Projects
    dataTable a nice header with a total book count and an "Add Project" button.
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
    This widget draws update form for a
    :py:class:`sphinx_hosting.models.Project`.
    """
    title: str = "General Settings"
    name: str = 'project-detail__section'
    modifier: str = 'general'
    icon: str = "card-checklist"
    css_class: str = CrispyFormWidget.css_class + " p-4"


#------------------------------------------------------
# Version related widgets
#------------------------------------------------------

class VersionInfoWidget(CardWidget):

    title: str = "Version Info"
    icon: str = "info-square"

    def __init__(self, version: Project, **kwargs):
        super().__init__(**kwargs)
        grid = Datagrid()
        grid.add_item(
            title='Project',
            content=version.project.machine_name,
            link=version.project.get_absolute_url()
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
        self.add_column(Column(name='left', alignment='start'))
        self.add_column(Column(name='center', alignment='center'))
        self.add_column(Column(name='right', alignment='end'))
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
    #card_title: str = 'Table of Contents'

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

    css_class: str = 'sphinxpage-globaltoc mt-3'

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

