from collections.abc import Iterable as IterableABC
from copy import deepcopy
from typing import Iterable, List, Optional, Union

from django.templatetags.static import static
from wildewidgets import Block


class Container(Block):
    """
    Extends :py:class:`wildewidgets.Block`.

    A `Bootstrap container <https://getbootstrap.com/docs/5.2/layout/containers/>`_

    Example::

        >>> c = Container(size='lg')

    Keyword Args:
        size: The max viewport size for the container, in bootstrap sizes, or
            ``fluid``.

    Raises:
        ValueError: ``size`` was not one of the valid sizes
    """
    VALID_SIZES: List[str] = [
        'sm',
        'md',
        'lg',
        'xl',
        'xxl',
        'fluid'
    ]

    #: The max viewport size for the container, in bootstrap sizes, or
    #:``fluid``.
    size: Optional[str] = None

    def __init__(
        self,
        *blocks,
        size: str = None,
        **kwargs
    ):
        self.size = size if size else self.size
        if self.size and self.size not in self.VALID_SIZES:
            raise ValueError(
                f"\"{self.size}\" is not a valid container size.  Valid sizes: {', '.join(self.VALID_SIZES)}")
        super().__init__(*blocks, **kwargs)
        if not self._css_class:
            self._css_class = ''
        # IMPORTANT: the Tabler rules sometimes expect that the container-* class to
        # be the first class in the class list.  If it is not first, the CSS rules
        # change.  E.g.:
        #
        # .navbar-vertical.navbar-expand-lg > [class^="container"] {
        #     flex-direction: column;
        #     align-items: stretch;
        #     min-height: 100%;
        #     justify-content: flex-start;
        #     padding: 0;
        # }
        if not self.size:
            self._css_class = 'container ' + self._css_class
        else:
            self._css_class = f' container-{size}' + self._css_class


class Link(Block):
    """
    Extends :py:class:`wildewidgets.Block`.

    This is a simple ``<a>`` tag.  We made it into its own block because we need `<a>`
    tags so often.

    Example::

        >>> link = Link('click here', url='https://example.com')

    Keyword Args:
        contents: The contents of the ``<a>``.  This can be string, a
            :py:class:`Block`, or an iterable of strings and :py:class:`Block`
            objects.
        url: The URL of the ``<a>``
        title: The value of the ``title`` tag for the link
        role: The value of the ``role`` attribute for the link
        target: The target for this link, aka the context in which the linked
            resource will open.
    """

    tag: str = 'a'

    #: The contents of the ``<a>``.  This can be string, a :py:class:`Block`,
    #: or an iterable of strings and :py:class:`Block` objects.
    contents: Union[str, Block, Iterable[Union[str, Block]]] = None
    #: The URL of the ``<a>``
    url: str = '#'
    #: The value of the ``role`` attribute for the link
    role: str = 'link'
    #: The value of the ``title`` attribute for the link
    title: Optional[str] = None
    #: The target for this link, aka the context in which the linked resource
    #: will open.
    target: Optional[str] = None

    def __init__(
        self,
        *contents: Union[str, Block],
        url: str = None,
        role: str = None,
        title: str = None,
        target: str = None,
        **kwargs
    ):
        self.url = url if url else self.url
        self.role = role if role else self.role
        self.title = title if title else self.title
        self.target = target if target else self.target
        # FIXME: validate url
        # FIXME: validate that title and role are htmleescaped
        if contents:
            self.contents: Iterable[Union[str, Block]] = contents
        else:
            c = self.contents
            if isinstance(c, str):
                self.contents = [c]
            elif isinstance(c, Block):
                self.contents = [deepcopy(c)]
            elif isinstance(c, IterableABC):
                self.contents = deepcopy(c)
            else:
                self.contents = []
        super().__init__(*self.contents, **kwargs)
        self._attributes['href'] = self.url
        self._attributes['role'] = self.role
        if self.title:
            self._attributes['title'] = self.title
        if self.target:
            self._attributes['target'] = self.title


class Image(Block):
    """
    An ``<img>``::

        <img src="image.png" alt="My Image" width="100%">

    Keyword Args:
        src: the URL of the image.  Typically this will be something like
            ``static('myapp/images/image.png')`` The default is to use a
            placeholder image to remind you that you need to fix this.
        height: the value of the ``height`` attribute for the ``<img>``
        width: the value of the ``width`` attribute for the ``<img>``
        alt: the value of the ``alt`` tag for the ``<img>``. If this is not
            set either here or as a class attribute, we'll raise ``ValueError`` to
            enforce WCAG 2.0 compliance.

    Raises:
        ValueError: no ``alt`` was provided
    """

    tag: str = 'img'
    block: str = 'image'

    #: The URL of the image.  Typically this will be something like :
    #``static('myapp/images/image.png')``.  The default is to use a placeholder
    #: image to remind you that you need to fix this.
    src: str = static('sphinx_hosting/images/placeholder.png')
    #: the value of the ``width`` attribute for the <img>
    width: Optional[str] = None
    #: the value of the ``height`` attribute for the <img>
    height: Optional[str] = None
    #: The value of the ``alt`` tag for the <img>.  If this is not set either
    #: here or in our contructor kwargs, we'll raise ``ValueError`` (to enforce
    #: ADA)
    alt: Optional[str] = None

    def __init__(
        self,
        src: str = None,
        height: str = None,
        width: str = None,
        alt: str = None,
        **kwargs
    ):
        self.src = src if src else self.src
        # FIXME: validate src as a URL/Path
        self.width = width if width else self.width
        self.height = height if height else self.height
        self.alt = alt if alt else self.alt
        # FIXME: htmlescape alt
        super().__init__(**kwargs)
        if self.src:
            self._attributes['src'] = src
        if self.width:
            self._attributes['width'] = width
        if not self.alt:
            raise ValueError('you must provide an "alt" attribute for your image')
        self._attributes['alt'] = self.alt


class LinkedImage(Link):
    """
    Extends :py:class:`Link`.

    An ``<img>`` wrapped in an ``<a>``::

        <a href="#">
            <img src="image.png" alt="My Image" width="100%">
        </a>

    Note:

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

    Raises:
        ValueError: no ``alt`` was provided

    """

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

    def __init__(
        self,
        image_src: str = None,
        image_width: str = None,
        image_alt: str = None,
        **kwargs
    ):
        self.image_src = image_src if image_src else self.image_src
        self.image_width = image_width if image_width else self.image_width
        self.image_alt = image_alt if image_alt else self.image_alt
        #: The actual image block that we will wrap with an ``<a>``
        self.image: Image = Image(src=self.image_src, width=self.image_width, alt=self.image_alt)
        super().__init__(self.image, **kwargs)
