from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple, Type, Union, cast

from django.db.models import Model, QuerySet
from django.db.models.functions import Length
from django.templatetags.static import static
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from wildewidgets import (
    BasicModelTable,
    Block,
    BreadrumbBlock,
    CardWidget,
    CrispyFormWidget,
    CrispyFormModalWidget,
    HTMLWidget,
    LightMenu,
    VerticalDarkMenu,
    Widget,
    WidgetListLayoutHeader,
)

from .forms import ProjectCreateForm
from .models import Project, SphinxPage, Version

MenuItem = Union[Tuple[str, str], Tuple[str, str, Dict[str, str]]]
DatagridItemDef = Union["DatagridItem", Tuple[str, str], Tuple[str, str, Dict[str, Any]]]


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


class SphinxPagePagination(LightMenu):

    navbar_classes = LightMenu.navbar_classes + ' submenu'

    def __init__(self, page: SphinxPage, **kwargs):
        super().__init__(page.title, **kwargs)
        self.items: List[MenuItem] = deepcopy(self.__class__.items)
        if page.parent:
            self.items.append(
                (f'Up: {page.parent.title}', page.parent.get_absolute_url())
            )
        if hasattr(page, 'previous_page'):
            self.items.append(
                (f'Prev: {page.previous_page.title}', page.previous_page.get_absolute_url())
            )
        if page.next_page:
            self.items.append(
                (f'Next: {page.next_page.title}', page.next_page.get_absolute_url())
            )

    def build_menu(self) -> None:
        """
        Here we're overriding :py:meth:`wildewidgets.BasicMenu.build_menu` to
        deal with bare URLs in addition to named URLPaths.
        """
        if len(self.active_hierarchy) > 0:
            for item in self.items:
                data = {}
                if isinstance(item[1], str):
                    try:
                        # Try to get this as a named URL from our URLConf
                        data['url'] = reverse(item[1])
                    except NoReverseMatch:
                        # It wasn't a named URL -- use it verbatim as a URL
                        data['url'] = item[1]
                    data['extra'] = ''
                    data['kind'] = 'item'
                    if len(item) > 2:
                        item = cast(Tuple[str, str, Dict[str, str]], item)
                        extra = item[2]
                        if isinstance(extra, dict):
                            extra_list = [f"{k}={v}" for k, v in extra.items()]
                            data['extra'] = f"?{'&'.join(extra_list)}"
                elif isinstance(item[1], list):
                    submenu_active = None
                    if len(self.active_hierarchy) > 1:
                        submenu_active = self.active_hierarchy[1]
                    data = self.parse_submemu(item[1], submenu_active)
                self.add_menu_item(item[0], data, item[0] == self.active_hierarchy[0])


#------------------------------------------------------
# Modals
#------------------------------------------------------

class ProjectCreateModalWidget(CrispyFormModalWidget):
    """
    This is a modal dialog that holds the
    :py:class:`sphinx_hosting.forms.ProjectCreateForm`.
    """

    modal_id = "project__create"
    modal_title = "Add Project"

    def __init__(self, *args, **kwargs):
        form = ProjectCreateForm()
        super().__init__(form=form, *args, **kwargs)


#------------------------------------------------------
# Widgets
#------------------------------------------------------

class DatagridItem(Block):
    """
    This widget implements a `Tabler datagrid-item <https://preview.tabler.io/docs/datagrid.html`_
    It should be used with :py:class:`Datagrid`.

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
        items:a list of ``datagrid-items`` to add to our content
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


class TwoColumnLayoutWidget(Block):

    block: str = 'two-column'
    css_class: Optional[str] = 'row'
    column_one_width = 3
    column_one_widgets: List[Widget] = []
    column_two_widgets: List[Widget] = []

    def __init__(self, **kwargs):
        column_one_width = kwargs.pop('column_one_width', self.column_one_width)
        self.column_one = Block(
            *kwargs.pop('column_one_widgets', self.column_one_widgets),
            name="two-column__column",
            modifier="one",
            css_class=f'col-{column_one_width}'
        )
        self.column_two = Block(
            *kwargs.pop('column_two_widgets', self.column_two_widgets),
            name="two-column__column",
            modifier="two",
            css_class='col'
        )
        super().__init__(**kwargs)
        self.add_block(self.column_one)
        self.add_block(self.column_two)

    def add_column_one_widget(self, widget: Widget):
        self.column_one.add_block(widget)

    def add_column_two_widget(self, widget: Widget):
        self.column_two.add_block(widget)


#------------------------------------------------------
# Project related widgets
#------------------------------------------------------

class ProjectInfoWidget(CardWidget):

    title = "Project Info"
    icon = "info-square"

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
    title = "Projects"
    icon = "window"

    def __init__(self, **kwargs):
        super().__init__(widget=ProjectTable(), **kwargs)

    def get_title(self):
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
    title = "Versions"
    icon = "bookmark-star"

    def __init__(self, project_id: int, **kwargs):
        self.project_id = project_id
        super().__init__(
            widget=ProjectVersionTable(project_id=project_id),
            **kwargs,
        )

    def get_title(self):
        header = WidgetListLayoutHeader(
            header_text="Versions",
            badge_text=Project.objects.get(pk=self.project_id).versions.count(),
        )
        return header


class ProjectDetailWidget(
    CrispyFormWidget,
    Widget
):
    title = "General Settings"
    name = 'project-detail__section'
    modifier = 'general'
    icon = "card-checklist"
    css_class = CrispyFormWidget.css_class + " p-4"


#------------------------------------------------------
# Version related widgets
#------------------------------------------------------

class VersionInfoWidget(CardWidget):

    title = "Version Info"
    icon = "info-square"

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
    title = "Pages"
    icon = "bookmark-star"

    def __init__(self, version_id: int, **kwargs):
        self.version_id = version_id
        super().__init__(
            widget=VersionSphinxPageTable(version_id=version_id),
            **kwargs,
        )

    def get_title(self):
        header = WidgetListLayoutHeader(
            header_text="Pages",
            badge_text=Version.objects.get(pk=self.version_id).pages.count(),
        )
        return header


#------------------------------------------------------
# SphinxPage related widgets
#------------------------------------------------------


class SphinxPageBodyWidget(HTMLWidget):

    css_class: str = 'sphinxpage-body'

    def __init__(self, page: SphinxPage, **kwargs):
        super().__init__(self, **kwargs)
        self.html = page.body


class SphinxPageTableOfContentsWidget(CardWidget):

    css_class: str = 'sphinxpage-toc'
    card_title: str = 'Table of Contents'

    def __init__(self, page: SphinxPage, **kwargs):
        super().__init__(**kwargs)
        self.widget = HTMLWidget(html=page.local_toc)


class SphinxPageLayout(TwoColumnLayoutWidget):
    """
    The page layout for a single :py:class:`sphinx_hosting.models.SphinxPage`.  It
    consists of a two column layout with the page's table of contents in the left
    column, and the content of the page in the right column.

    Args:
        page: the ``SphinxPage`` to render
    """

    column_one_width: int = 4

    def __init__(self, page: SphinxPage, **kwargs):
        super().__init__(**kwargs)
        self.add_column_one_widget(SphinxPageTableOfContentsWidget(page))
        self.add_column_two_widget(SphinxPageBodyWidget(page))


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
