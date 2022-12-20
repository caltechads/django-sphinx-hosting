from copy import deepcopy
from dataclasses import dataclass, field
import re
from typing import Dict, Iterable, List, Optional, Union

from wildewidgets import Block, CollapseWidget

from .basic import Container, Link, LinkedImage
from .icons import FontIcon


# ==============================
# Dataclasses
# ==============================

@dataclass
class MenuItem:
    """
    A menu item definition for a :py:class:`SidebarMenu`.  :py:attr:`title` is
    required, but the :py:attr:`icon` and :py:attr:`url` are not.

    Note:
        We're defining this dataclass so that you don't need to build out the
        entire menu system with the appropriate blocks yourself, but instead can
        nest :py:class:`MenuItem` objects and have us do it for you.

    If no :py:attr:`url` is provided, we will consider this item to be a section
    title in the menu.
    """

    #: The text for the item.  If ``url`` is not defined, this will define
    #: a heading within the menu
    text: str
    #: this is either the name of a bootstrap icon, or a :py:class:`Block`
    icon: Optional[Union[str, Block]] = None
    #: The URL for the item.  For Django urls, you will typically do something like
    #: ``reverse('myapp:view')`` or ``reverse_lazy('myapp:view')``
    url: Optional[str] = None
    #: a submenu under this menu item
    items: Iterable["MenuItem"] = field(default_factory=list)


# ==============================
# Blocks
# ==============================

class NavigationTogglerButton(Block):
    """
    Extends :py:class:`wildewidgets.Block`.

    The ``navbar-toggler`` button for hiding and showing menus in responsive
    `Bootstrap Navbar containers
    <https://getbootstrap.com/docs/5.2/components/navbar/#responsive-behaviors>`_
    ,  styled with some Tabler styling. This is the hamburger icon that causes
    the menus to appear and disappear when we drop below a specific viewport
    size.

    Example::

        >>> toggler = NavigationTogglerButton(target='the_target')

    Keyword Args:
        target: the CSS id of the tag to toggle
        label: the ARIA label of this button
    """

    tag: str = 'button'
    block: str = 'navbar-toggler'
    css_classes: str = 'collapsed'
    attributes: Dict[str, str] = {'type': 'button'}
    data_attributes: Dict[str, str] = {'toggle': 'collapse'}
    aria_attributes: Dict[str, str] = {'expanded': 'false'}

    #: The CSS id of the tag that this button toggles
    target: Optional[str] = None
    #: The ARIA label for this button
    label: str = 'Toggle navigation'

    def __init__(self, target: str = None, label: str = None, **kwargs):
        self.target = target if target else self.__class__.target
        self.label = label if label else self.__class__.label
        if not self.target:
            raise ValueError(
                'No target supplied; define it either as a constructor kwarg or as a class attribute'
            )
        super().__init__(**kwargs)
        self._aria_attributes['label'] = self.label
        self._aria_attributes['controls'] = self.target
        self._data_attributes['target'] = f"#{self.target.lstrip('#')}"
        self.add_block(
            Block(tag='span', name='navbar-toggler-icon')
        )


class Navbar(Block):
    """
    Extends :py:class:`wildewidgets.Block`.

    A horizontal `Bootstrap Navbar <https://getbootstrap.com/docs/5.2/components/navbar>`_.

    Examples:

        Class time configuration::

            class MyMenu(Menu):
                items = [MenuItem(text='One', url='/one', icon='target)]

            class MyNavbar(Navbar):
                branding = LinkedImage(src='/static/branding.png', alt='My Brand', url='#')
                contents = [MyMenu()]

        Constructor time configuration::

            >>> branding = LinkedImage(src='/static/branding.png', alt='My Brand', url='#')
            >>> items = [MenuItem(text='One', url='/one'), ... ]
            >>> menu = TablerMenu(*items)
            >>> sidebar = Navbar(menu, branding=branding)

        Adding menus later::

            >>> items2 = [MenuItem(text='Foo', url='/foo'), ... ]
            >>> menu2 = TablerMenu(*items)
            >>> sidebar.add_to_menu_section(menu2)

    Note:

        You can add other things to the menu section than just menus.  For instance,
        a search form::

            class SearchFormBlock(Block):
                ...

            class MyMenu(Menu):
                items = [MenuItem(text='One', url='/one', icon='target)]

            class MyNavbar(Navbar):
                branding = LinkedImage(src='/static/branding.png', alt='My Brand', url='#')
                contents = [SearchFormBlock(), MyMenu()]

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
        contents_id: the CSS id of the menu container.  Typically you won't need
            to change this unless you have namespace collisions with other CSS
            ids on your page.

    """
    tag: str = 'aside'
    block: str = 'navbar'

    VALID_BREAKPOINTS: List[str] = [
        size for size in Container.VALID_SIZES if size != 'fluid'
    ]
    #: Valid background colors.  Note that these are Tabler colors, not Bootstrap
    #: colors.  We use Tabler colors because Tabler also defines an appropriate
    #: foreground color for each background color.
    VALID_BACKGROUND_COLORS: List[str] = [
        'blue',
        'azure',
        'indigo',
        'purple',
        'pink',
        'red',
        'orange',
        'yellow',
        'lime',
        'green',
        'teal',
        'cyan',
    ]

    #: Set to ``True`` to use a dark background instead of light
    dark: bool = False
    #: If :py:attr:`dark` is ``True``, set the background color. Default: ``#1d273b``
    background_color: Optional[str] = None
    #: the CSS id of the menu container.  Typically you won't need
    #: to change this unless you have namespace collisions with other CSS
    #: ids on your page.
    contents_id: str = 'sidebar-menu'
    #: A block that will be displayed at the top of the container.
    #: A good choice might be a :py:class:`LinkedImage` or :py:class:`Image`
    branding: Optional[Block] = None
    #: A list of menus to include in our sidebar
    contents: Iterable[Block] = []
    #: The viewport size at which our menu container collapses to be hidden,
    #: requiring the hamburger menu to show
    hide_below_viewport: str = 'lg'
    #: The width of our actual navbar
    container_size: str = 'fluid'

    def __init__(
        self,
        *contents: Block,
        contents_id: str = None,
        branding: Block = None,
        hide_below_viewport: str = None,
        container_size: str = None,
        dark: bool = None,
        background_color: str = None,
        **kwargs
    ):
        self.contents_id = contents_id if contents_id else self.__class__.contents_id
        self.hide_below_viewport = hide_below_viewport if hide_below_viewport else self.__class__.hide_below_viewport
        self.container_size = container_size if container_size else self.__class__.container_size
        self.dark = dark if dark is not None else self.__class__.dark
        self.background_color = background_color if background_color is not None else self.__class__.background_color
        if contents:
            self.contents: Iterable[Block] = contents
        else:
            self.contents = deepcopy(self.__class__.contents)
        if self.hide_below_viewport not in self.VALID_BREAKPOINTS:
            raise ValueError(
                f'"{self.hide_below_viewport}" is not a valid breakpoint size. '
                f'Choose from: {", ".join(self.VALID_BREAKPOINTS)}'
            )
        if self.background_color and self.background_color not in self.VALID_BACKGROUND_COLORS:
            raise ValueError(
                f'"{self.bagckground_color}" is not a known color. '
                f'Choose from: {", ".join(self.VALID_BACKGROUND_COLORS)}'
            )

        super().__init__(**kwargs)
        if not self._css_class:
            self._css_class = ''
        # Set our hamburger menu breakpoint
        self._css_class += f' navbar-expand-{self.hide_below_viewport}'
        # light vs dark
        if self.dark:
            self._css_class += ' navbar-dark'
        # background color
        if self.background_color:
            self._css_class += f' bg-{self.background_color} bg-{self.background_color}-fg'
        # Set our "role" attribute to make us more accessible
        self._attributes['role'] = 'navigation'
        # Everything inside our sidebar lives in this inner container
        self.inner = Container(size=self.container_size, css_class='ms-0')
        self.add_block(self.inner)
        # The branding at top
        self.branding = branding if branding else deepcopy(self.__class__.branding)
        self.build_brand()
        # The menu toggler button for small viewports
        self.inner.add_block(NavigationTogglerButton(target=self.contents_id))
        # This is where all menus go
        self.menu_container = CollapseWidget(css_id=self.contents_id, css_class='navbar-collapse')
        self.inner.add_block(self.menu_container)
        for block in self.contents:
            self.add_to_menu_section(block)

    def build_brand(self) -> None:
        """
        Build our ``.navbar-brand`` block and add it to our content container.
        We're doing this in a method here so we can override it in subclasses.
        """
        if self.branding:
            if self.branding._css_class:
                # Add the .navbar-brand class (if it does not exist) to our
                # branding block to make it work properly within the .navbar
                if 'navbar-brand' not in self.branding._css_class:
                    self.branding._css_class += ' navbar-brand'
            else:
                self.branding._css_class = ' navbar-brand'
            self.inner.add_block(self.branding)

    def add_to_menu_section(self, block: Block) -> None:
        """
        Add a block to the menu specfic section of the sidebar.  The menu
        specific section will be hidden and controlled by the hamburger menu
        when we drop below a specific viewport.

        Args:
            block: the block to add to the menu section
        """
        self.menu_container.add_block(block)


class TablerVerticalNavbar(Navbar):
    """
    Extends :py:class:`Nabvar`.

    Make this a Tabler vertical dark navbar.

    * Make the navbar vertical instead of horizontal
    * :py:attr:`dark` is always ``True``
    * Fix width of sidebar at 15rem
    * CSS ``position`` is always ``fixed``.
    * Supply some open/close animations.

    Some caveats:

    * :py:attr:`container_size` is ignored

    Example:

        >>> branding = LinkedImage(src='/static/branding.png', alt='My Brand', url='https://example.com')
        >>> items = [MenuItem(text='One', url='/one'), ... ]
        >>> menu = TablerMenu(*items)
        >>> sidebar = TablerVerticalNavbar(menu, branding=branding)
    """
    css_class: str = 'navbar-vertical'
    dark: bool = True

    def build_brand(self) -> None:
        """
        Overrides :py:meth:`Navbar.build_brand`.

        Wrap our branding in an ``<h1>`` and give that ``<h1>`` the
        ``navbar-brand`` class because that's how Tabler does it.
        """
        brand_container = Block(self.branding, tag='h1', css_class='navbar-brand navbar-brand-autodark')
        self.inner.add_block(brand_container)


class TablerMenuIcon(FontIcon):
    """
    Extends :py:class:`sphinx_hosting.wildewidgets.FontIcon`.

    A Tabler menu specific icon.  This just adds some menu specific classes and
    uses a ``<span>`` instead of a ``<i>``.  It is used by :py:class:`NavItem`,
    :py:class:`NavDropdownItem` and :py:class:`DropdownItem` objects.

    Typically, you won't use this directly, but instead it will be created for
    you from a :py:class:`MenuItem` specification when :py:class:`MenuItem.icon`
    is not ``None``.

    Example:

        >>> icon = TablerMenuIcon(icon='target')
        >>> item = NavItem(text='Page', url='/page', icon=icon)
        >>> item2 = DropdownItem(text='Page', url='/page', icon=icon)
        >>> item3 = NavDropdownItem(text='Page', url='/page', icon=icon)
    """

    tag: str = 'span'
    block: str = 'nav-link-icon'
    css_classes: str = 'd-md-none d-lg-inline-block'


class MenuHeading(Block):
    """
    Extends :py:class:`wildewidgets.Block`.

    A Tabler menu specific heading.  This is a heading within a menu that
    sepearates the actual menu items into groups.

    Typically, you won't use this directly, but instead it will be created for
    you from a :py:class:`MenuItem` specification when :py:attr:`MenuItem.url`
    is ``None``.

    Example:

        >>> heading = MenuHeading(text='My Heading')

    Kewyword Args:
        text: the text of the heading
    """

    block: str = 'nav-link'
    css_class: str = 'my-1 fw-bold text-uppercase'

    #: The text of the heading
    text: Optional[str] = None

    def __init__(self, text: str = None, **kwargs):
        self.text = text if text else self.__class__.text
        super().__init__(**kwargs)
        self.add_block(self.text)


class NavItem(Block):
    """
    Extends :py:class:`wildewidgets.Block`.

    An entry in a :py:class:`Menu`, the top level menu class used in a
    :py:class:`Navbar` in the menu section.  This is a label with a link to a
    URL, with an optional icon preceding the label.

    Typically, you won't use this directly, but instead it will be created for
    you from a :py:class:`MenuItem` specification.

    If :py:attr:`url` and the ``url`` kwarg are ``None``, this will be a heading
    instead of an item that links to a URL.

    Examples:

        With keyword arguments::

            >>> icon = TablerMenuIcon(icon='target')
            >>> item = NavItem(text='Page', url='/page', icon=icon)

        With a :py:class:`MenuItem`::

            >>> menu_item = MenuItem(text='Page', url='/page', icon='target')
            >>> item = NavItem(item=menu_item)

        Adding a heading::

            >>> item = NavItem(text='My Heading')
            >>> menu_item = MenuItem(text='Page')
            >>> item2 = NavItem(item=menu_item)

    Kewyword Args:
        icon: Either the name of a Bootstrap icon, or a
            :py:class:`TablerMenuIcon` object
        text: The text for the item
        url: The URL for the item

    Raises:
        ValueError: one or more of the settings failed validation
    """

    tag: str = 'li'
    block: str = 'nav-item'

    #: Either the name of a Bootstrap icon, or a :py:class:`TablerMenuIcon`
    #: object
    icon: Optional[Union[str, TablerMenuIcon]] = None
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
            icon_block = TablerMenuIcon(icon=self.icon)
        contents: Block
        if self.url:
            contents = Link(url=self.url, css_class='nav-link')
            if icon_block:
                contents.add_block(icon_block)
            contents.add_block(self.text)
        else:
            contents = MenuHeading(text=self.text)
        self.add_block(contents)


# Submenus:

class NavDropdownControl(Link):
    """
    Extends :py:class:`sphinx_hosting.wildewidgets.Link`.

    This is a dropdown control that opens a submenu from within either a
    :py:class:`Menu` or a :py:class`DropdownMenu` within a :py:class:`Menu`.  It
    consists of a label with optional icon in front, plus a arrow that toggles
    direction when the menu opens and closes.

    Examples:

        No icon:

        >>> control = NavDropdownControl(text='My Control')

        With an icon:

        >>> control = NavDropdownControl(text='My Control', icon='arrow-down-square-fill')

        With a :py:class:`TablerMenuIcon`:

        >>> arrow_icon = TablerMenuIcon(icon='arrow-down-square-fill')
        >>> control2 = NavDropdownControl(text='My Control', icon=arrow_icon)

    Keyword Args:
        icon: either the name of a Bootstrap icon, or a :py:class:`TablerMenuIcon`
            class or subclass
        text: The label for the dropdown control
        button_id: The CSS Id to assign to this button.  We need this to tie the
            button to the actual :py:class:`DropdownItem`

    Raises:
        ValueError: no ``text`` was supplied
    """

    block: str = 'nav-link'
    css_class: str = 'dropdown-toggle'
    data_attributes: Dict[str, str] = {
        'toggle': 'dropdown',
        'auto-close': 'true'
    }
    aria_attributes: Dict[str, str] = {
        'haspopup': 'true',
        'expanded': 'true'
    }
    #: Either the name of a Bootstrap icon, or a :py:class:`TablerMenuIcon`
    #: class or subclass
    icon: Optional[Union[str, TablerMenuIcon]] = None
    #: The actual name of the dropdown
    text: Optional[str] = None
    #: The CSS Id to assign to this button.  We need this to tie the button
    #: to the actual :py:class:`TablerDropdownItem`
    button_id: Optional[str] = None

    def __init__(
        self,
        text: str = None,
        icon: Union[str, TablerMenuIcon] = None,
        button_id: str = None,
        **kwargs
    ):
        self.text = text if text else self.__class__.text
        self.icon = icon if icon else deepcopy(self.__class__.icon)
        self.button_id = button_id if button_id else self.__class__.button_id
        if not self.text:
            raise ValueError('"text" is required as either a class attribute of a keyword arg')
        if not self.button_id:
            raise ValueError('"button_id" is required as either a class attribute of a keyword arg')
        super().__init__(css_id=self.button_id, role='button', **kwargs)
        if self.icon:
            self.add_block(TablerMenuIcon(icon=self.icon))
        self.add_block(self.text)


class DropdownItem(Link):
    """
    Extends :py:class:`sphinx_hosting.wildewidgets.Link`.

    An entry in a :py:class:`DropdownMenu`, a submenu class used in a
    :py:class:`NavDropdownItem` of a :py:class:`Menu`.  This is a
    label with a link to a URL, with an optional icon preceding the label.

    Typically, you won't use this directly, but instead it will be created for
    you from a :py:class:`MenuItem` specification when :py:attr:`MenuItem.url`
    is not ``None``.

    Examples:

        >>> icon = TablerMenuIcon(icon='target')
        >>> item = DropdownItem(text='Page', url='/page', icon=icon)

        >>> menu_item = MenuItem(text='Page', url='/page', icon='target')
        >>> item = DropdownItem(item=menu_item)

    Kewyword Args:
        icon: Either the name of a Bootstrap icon, or a
            :py:class:`TablerMenuIcon` object
        text: The text for the item

    Raises:
        ValueError: one or more of the settings failed validation
    """
    block: str = 'dropdown-item'
    css_class: str = 'ps-3'

    #: this is either the name of a bootstrap icon, or a :py:class:`TablerMenuIcon`
    #: class or subclass
    icon: Optional[Union[str, TablerMenuIcon]] = None
    #: The text for the item.
    text: Optional[str] = None

    def __init__(
        self,
        text: str = None,
        icon: str = None,
        item: MenuItem = None,
        **kwargs
    ):
        if item and (text or icon or kwargs.get('url', None)):
            raise ValueError('Specify "item" or ("text", "icon", "url"), but not both')
        if item:
            self.text = item.text
            self.icon = item.icon if item.icon else self.__class__.icon
            if item.url:
                kwargs['url'] = item.url
        else:
            self.text = text if text else self.__class__.text
            self.icon = icon if icon else self.__class__.icon
        if not self.text:
            raise ValueError('"text" is required as either a class attribute or keyword arg')
        if not self.url:
            raise ValueError('"url" is required as either a class attribute or keyword arg')
        super().__init__(**kwargs)
        icon_block: Block = None
        if self.icon:
            icon_block = TablerMenuIcon(icon=self.icon, css_class='text-white')
        if icon_block:
            self.add_block(icon_block)
        self.add_block(self.text)


# TODO: tabler dropdown divider

class DropdownMenu(Block):
    """
    Extends :py:class:`wildewidgets.Block`.

    A `Tabler dropdown menu <https://preview.tabler.io/docs/dropdowns.html>`_.

    Typically, you won't use this directly, but instead it will be created for
    you from a :py:class:`MenuItem` specification when :py:attr:`MenuItem.url`
    is not ``None``.

    Examples:

        >>> items = [
            MenuItem(text='One', url='/one', icon='1-circle'),
            MenuItem(text='Two', url='/two', icon='2-circle'),
            MenuItem(text='Three', url='/three', icon='3-circle'),
        ]
        >>> button = NavDropdownControl(
            text='My Dropdown Menu',
            icon='arrow-down-square-fill',
            button_id='my-button'
        )
        >>> menu = DropdownMenu(*items, button_id=button.button_id)

    Warning:

        Currently we don't support nested dropdown menus, so if you do this::

        >>> items = [
            MenuItem(
                text='One',
                icon='1-circle'
                items=[
                    MenuItem(text='Two', url='/two', icon='2-circle'),
                    MenuItem(text='Three', url='/three', icon='3-circle'),
                ]
            )
        ]
        >>> button = NavDropdownControl(
            text='My Dropdown Menu',
            icon='arrow-down-square-fill',
            button_id='my-button'
        )
        >>> menu = DropdownMenu(*items, button_id=button.button_id)

        You will just get a dropdown menu with a single item that does
        not link to anything.

    Args:
        *items: the list of :py:class:`MenuItem` objects to insert into
            this menu

    Keyword Args:
        button_id: it CSS id for the button

    Raises:
        ValueError: one or more of the settings failed validation
    """

    block: str = 'dropdown-menu'

    #: A list of :py:class:`MenuItem` objects to add to this dropdown menu
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
        if not self.button_id:
            raise ValueError('"button_id" is required as either a class attribute of a keyword arg')
        if items:
            self.items: Iterable[MenuItem] = items
        else:
            self.items = deepcopy(self.__class__.items)
        super().__init__(**kwargs)
        self._aria_attributes['labelledby'] = self.button_id
        for item in items:
            self.add_block(DropdownItem(item=item))

    def add_item(
        self,
        text: str = None,
        url: str = None,
        icon: Union[str, TablerMenuIcon] = None,
        item: MenuItem = None
    ) -> None:
        ...


class NavDropdownItem(Block):
    """
    Extends :py:class:`wildewidgets.Block`.

    An item in a :py:class:`Menu` that opens a dropdown submenu.

    Typically, you won't use this directly, but instead it will be created for
    you from a :py:class:`MenuItem` specification when :py:attr:`MenuItem.items`
    is not empty.

    Examples:

        >>> sub_items = [
            MenuItem(text='One', url='/one', icon='1-circle'),
            MenuItem(text='Two', url='/two', icon='2-circle'),
            MenuItem(text='Three', url='/three', icon='3-circle'),
        ]
        >>> item = NavDropdownItem(*sub_items, text='My Submenu', icon='target')
        >>> menu = Menu(item)


    Args:
        *items: the list of :py:class:`MenuItem` objects to insert into
            this menu

    Keyword Args:
        text: the text for the menu item
        icon: this is either the name of a Bootstrap icon, or a
            :py:class:`TablerMenuIcon` class or subclass

    Raises:
        ValueError: one or more of the settings failed validation
    """

    tag: str = 'li'
    block: str = 'nav-item'
    css_class: str = 'dropdown'

    #: this is either the name of a bootstrap icon, or a :py:class:`MenuIcon`
    #: class or subclass
    icon: Optional[Union[str, TablerMenuIcon]] = None
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
        button_id = re.sub('[ ._]', '-', button_id)
        self.add_block(NavDropdownControl(button_id=button_id, text=self.text, icon=icon))
        self.add_block(DropdownMenu(*self.items, button_id=button_id))


class Menu(Block):
    """
    Extends :py:class:`wildewidgets.Block`.

    An `Bootstrap ``.navbar-nav`` <https://getbootstrap.com/docs/5.2/components/navbar/>`_ for
    use in a :py:class:`Navbar`.

    Use this in any of these ways:

    * Subclass :py:class:`Menu` and define :py:attr:`items`
    * Pass in the ``items`` kwargs to the constructor
    * Add items with :py:meth:`add_item`
    * Subclass :py:class:`Menu`, define :py:attr:`items`, and add additional items with
      :py:meth:`add_item

    Examples:

        Subclassing::

            class MyMenu(Menu):

                items = [
                    MenuItem(text='One', url='/one', icon='1-circle'),
                    MenuItem(text='Two', url='/two', icon='2-circle'),
                    MenuItem(text='Three', url='/three', icon='3-circle'),
                ]

        Constructor::

            >>> menu = Menu(
                MenuItem(text='One', url='/one', icon='1-circle'),
                MenuItem(text='Two', url='/two', icon='2-circle'),
                MenuItem(text='Three', url='/three', icon='3-circle'),
            )

        ``Menu.add_item``::

            >>> menu = Menu()
            >>> menu.add_item(MenuItem(text='One', url='/one', icon='1-circle'))
            >>> menu.add_item(MenuItem(text='Two', url='/two', icon='2-circle'))
            >>> menu.add_item(MenuItem(text='Three', url='/three', icon='3-circle'))

    Args:
        *items: the list of :py:class:`MenuItem` objects to insert into
            this menu

    Raises:
        ValueError: one or more of the settings failed validation
    """

    tag: str = 'ul'
    block: str = 'navbar-nav'
    css_class: str = 'me-1'

    #: The list of items in this menu
    items: Iterable[MenuItem] = []

    def __init__(
        self,
        *items: MenuItem,
        **kwargs
    ):
        if items:
            self._items: List[MenuItem] = list(items)
        else:
            self._items = list(deepcopy(self.__class__.items))
        super().__init__(**kwargs)

    def get_content(self, **kwargs) -> str:
        # FIXME: why am I doing this in get_content() instead of in __init__()
        self.build_menu(self._items)
        return super().get_content(**kwargs)

    def build_menu(self, items: Iterable[MenuItem]) -> None:
        """
        Recurse through ``items`` and build out our menu and any submenus.

        For each ``item`` in ``items``, if ``item.items`` is not empty, add a
        submenu, otherwise add simple item.

        Args:
            items: the list of menu items to add to the list
        """
        for item in items:
            if item.items:
                self.add_block(NavDropdownItem(*item.items, text=item.text, icon=item.icon))
            else:
                self.add_block(NavItem(item=item))

    def add_item(self, item: MenuItem) -> None:
        """
        Add a single :py:class:`MenuItem` to ourselves.

        Args:
            item: the menu item to add to ourselves.
        """
        self._items.append(item)
