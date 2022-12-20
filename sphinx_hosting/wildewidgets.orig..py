from copy import copy, deepcopy
from dataclasses import dataclass, field
from functools import partial
import re
from typing import Any, Dict, Iterable, List, Optional, Tuple, Type, Union

from django.core.exceptions import ImproperlyConfigured
from django.db.models import Model, QuerySet
from django.db.models.functions import Length
from django.templatetags.static import static
from django.urls import reverse, reverse_lazy
from wildewidgets import (
    BasicModelTable,
    Block,
    BreadrumbBlock,
    CardHeader,
    CardWidget,
    CollapseWidget,
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
            col = f' col-12 col-md-{self.width}'
        if self._css_class is None:
            self._css_class = ''
        self._css_class += col
        if self.alignment:
            self._css_class += f' d-flex flex-column align-items-{self.alignment}'


class Row(Block):
    """
    This widget implements a ``row`` from the `Bootstrap Grid system
    <https://getbootstrap.com/docs/5.2/layout/grid/>`_.

    As columns are added to this Row, helper methods are also added
    to this :py:class:`row` instance, named for the :py:attr:`Column.name`
    of the column.  See :py:meth:`_add_helper_method`.

    Args:
        columns: a list of :py:class:`Column` objects
    """

    block: str = 'row'

    #: A list of :py:class:`Column` blocks to add to the this row
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
        Return the list of :py:attr:`Column.name` attributes of all of our
        columns.

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

    tag: str = 'i'
    block: str = 'fonticon'

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
        if self._css_class is None:  # type: ignore
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


class Image(Block):
    """
    An ``<img>``::

        <img src="image.png" alt="My Image" width="100%">

    Keyword Args:
        src: the URL of the image.  Typically this will be something like
            ``static('myapp/images/image.png')``
        width: the value of the ``width`` attribute for the ``<img>``
        alt: the value of the ``alt`` tag for the ``<img>``. If this is not
            set either here or as a class attribute, we'll raise ``ValueError`` to
            enforce WCAG 2.0 compliance.

    Raises:
        ValueError: no ``alt`` was provided
    """

    tag: str = 'img'
    block: str = 'image'

    #: The URL of the image.  Typically this will be something like
    #: ``static('myapp/images/image.png')``
    src: str = static('sphinx_hosting/images/placeholder.png')
    #: the value of the ``width`` attribute for the <img>
    width: Optional[str] = None
    #: The value of the ``alt`` tag for the <img>.  If this is not set either
    #: here or in our contructor kwargs, we'll raise ``ValueError`` (to enforce
    #: ADA)
    alt: Optional[str] = None

    def __init__(
        self,
        src: str = None,
        width: str = None,
        alt: str = None,
        link_url: str = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.src = src if src else self.__class__.src
        self.width = width if width else self.__class__.width
        self.alt = alt if alt else self.__class__.alt
        if self.src:
            self._attributes['src'] = src
        if self.width:
            self._attributes['width'] = width
        if not self.alt:
            raise ValueError('you must provide an "alt" attribute for your image')
        self._attributes['alt'] = self.alt


class LinkedImage(Block):
    """
    An ``<img>`` wrapped in an ``<a>``::

        <a href="#">
            <img src="image.png" alt="My Image" width="100%">
        </a>

    .. note::

        If you want to modify the encapsulated image (to add css classes, for
        example), you can do so by modifying the attributes on :py:attr:`image`
        after constructing the ``LinkedImage``::

            >>> b = LinkedImage(image_src='image.png', image_alt='My Image',
                url='http://example.com')
            >>> b.image._css_class = 'my-extra-class'
            >>> b.image._css_id = 'the-image'

    Attributes:
        image: the constructed :py:class:`Image` block

    Keyword Args:
        image_src: the URL of the image.  Typically this will be something like
            ``static('myapp/images/image.png')``
        image_width: the value of the ``width`` attribute for the ``<img>``
        image_alt: the value of the ``alt`` tag for the ``<img>``. If this is not
            set either here or as a class attribute, we'll raise ``ValueError`` to
            enforce WCAG 2.0 compliance.
        url: the URL to send the user to when they click the image.

    Raises:
        ValueError: no ``alt`` was provided

    """

    tag: str = 'a'
    block: str = 'linked-image'

    #: The URL of the image.  Typically this will be something like
    #: ``static('myapp/images/image.png')``
    image_src: str = static('sphinx_hosting/images/placeholder.png')
    #: the value of the ``width`` attribute for the ``<img>``.
    image_width: Optional[str] = None
    #: The value of the ``alt`` tag for the ``<img>``.  If this is not set either
    #: here or in our contructor kwargs, we'll raise ``ValueError`` to enforce
    #: WCAG 2.0 compliance.
    image_alt: Optional[str] = None
    #: The URL to send the user to when they click the image.
    url: Optional[str] = '#'

    def __init__(
        self,
        image_src: str = None,
        image_width: str = None,
        image_alt: str = None,
        url: str = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.image_src = image_src if image_src else self.__class__.image_src
        self.image_width = image_width if image_width else self.__class__.image_width
        self.image_alt = image_alt if image_alt else self.__class__.image_alt
        #: The actual image block that we will wrap with an ``<a>``
        self.image: Image = Image(src=self.image_src, width=self.image_width, alt=self.image_alt)
        self.url = url if url else self.__clas__.url
        self.add_block(self.image)
        self._attributes['href'] = self.url


class NavigationTogglerButton(Block):
    """
    This is purely a ``<button>`` that toggles visibility on another tag when
    we're below a certain viewpoint size.  Typically, you would use it to toggle
    visibility on a main menu when using the site on a phone.

    Keyword Args:
        target_id: the CSS id of the tag to toggle
        label: the ARIA label of this button
    """

    tag: str = 'button'
    block: str = 'navbar-toggler'
    css_classes: str = 'collapsed'
    attributes: Dict[str, str] = {'type': 'button'}
    data_attributes: Dict[str, str] = {'toggle': 'collapse'}
    aria_attributes: Dict[str, str] = {'expanded': 'false'}

    #: The CSS id of the tag that this button toggles
    target_id: Optional[str] = None
    #: The ARIA label for this button
    label: str = 'Toggle navigation'

    def __init__(self, target_id: str = None, label: str = None, **kwargs):
        self.target_id = target_id if target_id else self.__class__.target_id
        self.label = label if label else self.__class__.label
        if not self.target_id:
            raise ValueError(
                'No target_id supplied; define it either as a constructor kwarg or as a class attribute'
            )
        super().__init__(**kwargs)
        self._aria_attributes['label'] = self.label
        self._aria_attributes['controls'] = self.target_id
        self._data_attributes['target'] = f"#{self.target_id}"
        self.add_block(
            Block(tag='span', name='navbar-toggler-icon')
        )


class NavigationSidebar(Block):
    """
    A container block for the vertical dark left menu space on the page.  This
    allows us to place any arbitrary block in the menu space.

    Args:
        *blocks: a list of :py:class:`wildewidget.Block` (or subclass) instances to
            be added to this container

    Keyword Args:
        branding: A block that will be displayed at the top of the container.
            A good choice might be a :py:class:`LinkedImage` or :py:class:`Image`
        logo_width: The width for the logo image.  Any valid value
            for CSS ``width`` will be accepted.
        title: A title.  If ``logo`` is ``None``, this will be used in its
            place. If `logo` is not ``None``, this will be used as the image ``alt``
            attribute.

    """
    tag: str = 'aside'
    block: str = 'navbar'
    css_class: str = 'navbar-vertical navbar-expand-lg navbar-dark'
    contents_id: str = 'sidebar-menu'

    #: A block that will be displayed at the top of the container.
    #: A good choice might be a :py:class:`LinkedImage` or :py:class:`Image`
    branding: Optional[Block] = None

    #: A list of menus to include in our sidebar
    contents: Iterable[Block] = []

    def __init__(
        self,
        *contents: Block,
        contents_id: str = None,
        branding: Block = None,
        **kwargs
    ):
        self.contents_id = contents_id if contents_id else self.__class__.contents_id
        if contents:
            self.contents: Iterable[Block] = contents
        else:
            self.contents = deepcopy(self.__class__.contents)
        super().__init__(**kwargs)
        # Everything inside our sidebar lives in this inner container
        self.inner = Block(css_class='container-lg ms-0')
        self.add_block(self.inner)
        # The branding at top
        self.branding = branding if branding else deepcopy(self.__class__.branding)
        if self.branding:
            if self.branding._css_class:
                if 'navbar-brand' not in self.branding._css_class:
                    self.branding._css_class += ' navbar-brand'
            else:
                self.branding._css_class = ' navbar-brand'
            self.inner.add_block(self.branding)
        # The menu toggler button for small viewports
        self.inner.add_block(NavigationTogglerButton(target_id=self.contents_id))
        # This is where all menus go
        self.menu_container = CollapseWidget(css_id=self.contents_id, css_class='navbar-collapse')
        self.inner.add_block(self.menu_container)
        for block in self.contents:
            self.menu_container.add_block(block)


@dataclass
class MenuItem:
    """
    A menu item for a :py:class:`SidebarMenu`.  :py:attr:`title` is required, but
    the :py:attr:`icon` and :py:attr:`url` are not.

    If no :py:attr:`url` is provided, we will consider this item to be a section
    title in the menu.
    """

    #: The text for the item.
    text: str
    #: this is either the name of a bootstrap icon, or a :py:class:`Block`
    icon: Optional[Union[str, Block]] = None
    #: The URL for the item.  For Django urls, you will typically do something like
    #: ``reverse('myapp:view')`` or ``reverse_lazy('myapp:view')``
    url: Optional[str] = None
    #: a submenu under this menu item
    items: Iterable["MenuItem"] = field(default_factory=list)


class MenuIcon(FontIcon):

    tag: str = 'span'
    block: str = 'nav-link-icon'
    css_classes: str = 'd-md-none d-lg-inline-block'


class MenuHeading(Block):

    block: str = 'nav-link'
    css_class: str = 'my-1 fw-bold text-uppercase'
    text: Optional[str] = None

    def __init__(self, text: str = None, **kwargs):
        self.text = text if text else self.__class__.text
        super().__init__(**kwargs)
        self.add_block(self.text)


class TablerNavItem(Block):

    tag: str = 'li'
    block: str = 'nav-item'

    #: this is either the name of a bootstrap icon, or a :py:class:`FontIcon`
    #: class or subclass
    icon: Optional[Union[str, MenuIcon]] = None
    #: The text for the item.
    text: Optional[str] = None
    #: The URL for the item.
    url: Optional[str] = None

    def __init__(
        self,
        text: str = None,
        icon: str = None,
        url: str = None,
        item: MenuItem = None,
        **kwargs
    ):
        if item and (text or icon or url):
            raise ValueError('Specify "item" or ("text", "icon", "url"), but not both')
        if item:
            self.text = item.text
            self.icon = item.icon if item.icon else deepcopy(self.__class__.icon)
            self.url = item.url if item.url else self.__class__.url
        else:
            self.text = text if text else self.__class__.text
            self.icon = icon if icon else self.__class__.icon
            self.url = url if url else self.__class__.url
            if not self.text:
                raise ValueError('"text" is required as either a class attribute or keyword arg')
        super().__init__(**kwargs)
        icon_block: Block = None
        if self.icon:
            icon_block = MenuIcon(icon=self.icon)
        contents: Block
        if self.url:
            contents = Block(tag='a', attributes={'href': self.url}, css_class='nav-link')
            if icon_block:
                contents.add_block(icon_block)
            contents.add_block(self.text)
        else:
            contents = MenuHeading(text=self.text)
        self.add_block(contents)


class TablerNavDropdownControl(Block):

    tag: str = 'a'
    block: str = 'nav-link'
    css_class: str = 'dropdown-toggle'
    attributes: Dict[str, str] = {'role': 'button'}
    data_attributes: Dict[str, str] = {
        'toggle': 'dropdown',
        'auto-close': 'true'
    }
    aria_attributes: Dict[str, str] = {
        'haspopup': 'true',
        'expanded': 'true'
    }
    #: this is either the name of a bootstrap icon, or a :py:class:`MenuIcon`
    #: class or subclass
    icon: Optional[Union[str, MenuIcon]] = None
    #: The actual name of the dropdown
    text: Optional[str] = None

    def __init__(
        self,
        text: str = None,
        icon: Union[str, MenuIcon] = None,
        **kwargs
    ):
        self.text = text if text else self.__class__.text
        self.icon = icon if icon else deepcopy(self.__class__.icon)
        if not self.text:
            raise ValueError('"text" is required as either a class attribute of a keyword arg')
        super().__init__(**kwargs)
        if self.icon:
            self.add_block(MenuIcon(icon=self.icon))
        self.add_block(self.text)


class TablerDropdownItem(Block):

    tag: str = 'a'
    block: str = 'dropdown-item'
    css_class: str = 'ps-3 bg-white-lt'

    #: this is either the name of a bootstrap icon, or a :py:class:`MenuIcon`
    #: class or subclass
    icon: Optional[Union[str, MenuIcon]] = None
    #: The text for the item.
    text: Optional[str] = None
    #: The URL for the item.
    url: Optional[str] = None

    def __init__(
        self,
        text: str = None,
        icon: str = None,
        url: str = None,
        item: MenuItem = None,
        **kwargs
    ):
        if item and (text or icon or url):
            raise ValueError('Specify "item" or ("text", "icon", "url"), but not both')
        if item:
            self.text = item.text
            self.icon = item.icon if item.icon else self.__class__.icon
            self.url = item.url if item.url else self.__class__.url
        else:
            self.text = text if text else self.__class__.text
            self.icon = icon if icon else self.__class__.icon
            self.url = url if url else self.__class__.url
        if not self.text:
            raise ValueError('"text" is required as either a class attribute or keyword arg')
        if not self.url:
            raise ValueError('"url" is required as either a class attribute or keyword arg')
        super().__init__(**kwargs)
        self._attributes['href'] = self.url
        icon_block: Block = None
        if self.icon:
            icon_block = MenuIcon(icon=self.icon, css_class='text-white')
        if icon_block:
            self.add_block(icon_block)
        self.add_block(self.text)


class TablerDropdownMenu(Block):

    block: str = 'dropdown-menu'

    #: A list of items to add to this dropdown menu
    items: Iterable[MenuItem] = []
    #: The id of the dropdown-toggle button that controls this menu
    button_id: Optional[str] = None

    def __init__(
        self,
        *items: MenuItem,
        button_id: str = None,
        **kwargs
    ):
        self.button_id = button_id if button_id else self.__class__.button_id
        if items:
            self.items: Iterable[MenuItem] = items
        else:
            self.items = deepcopy(self.__class__.items)
        super().__init__(**kwargs)
        self._aria_attributes['labelledby'] = self.button_id
        for item in items:
            self.add_block(TablerDropdownItem(item=item))


class TablerNavDropdown(Block):

    tag: str = 'li'
    block: str = 'nav-item'
    css_class: str = 'dropdown'

    #: this is either the name of a bootstrap icon, or a :py:class:`MenuIcon`
    #: class or subclass
    icon: Optional[Union[str, MenuIcon]] = None
    #: The actual name of the dropdown
    text: Optional[str] = None
    #: The list of items in this dropdown menu
    items: Iterable[MenuItem] = []

    def __init__(
        self,
        *items: MenuItem,
        text: str = None,
        icon: str = None,
        **kwargs
    ):
        self.text = text if text else self.__class__.text
        self.icon = self.icon if self.icon else deepcopy(self.__class__.icon)
        if not self.text:
            raise ValueError('"text" is required as either a class attribute of a keyword arg')
        if items:
            self.items: Iterable[MenuItem] = items
        else:
            self.items = deepcopy(self.__class__.items)
        super().__init__(*kwargs)
        button_id = f'nav-item-{self.text.lower()}'
        self.add_block(TablerNavDropdownControl(css_id=button_id, text=self.text, icon=icon))
        self.add_block(TablerDropdownMenu(*self.items, button_id=button_id))


class TablerMenu(Block):

    tag: str = 'ul'
    block: str = 'navbar-nav'
    css_class: str = 'me-1'

    #: The list of items in this menu
    items: Iterable[MenuItem] = []
    #: The title for this menu, if any
    title: Optional[str] = None

    def __init__(
        self,
        *items: MenuItem,
        title: str = None,
        **kwargs
    ):
        if items:
            self.items: Iterable[MenuItem] = items
        else:
            self.items = deepcopy(self.__class__.items)
        super().__init__(**kwargs)

    def get_content(self, **kwargs) -> str:
        self.build_menu(self.items)
        return super().get_content(**kwargs)

    def build_menu(self, items: Iterable[MenuItem]) -> None:
        """
        Recurse through ``items`` and build out our menu and any submenus.

        Args:
            items: the list of menu items to add to the list
        """
        for item in items:
            if item.items:
                self.add_block(TablerNavDropdown(*item.items, text=item.text, icon=item.icon))
            else:
                self.add_block(TablerNavItem(item=item))

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

