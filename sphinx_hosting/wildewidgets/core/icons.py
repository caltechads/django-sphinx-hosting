from typing import Optional

from wildewidgets import Block


class FontIcon(Block):
    """
    Extends :py:class:`wildewidgets.Block`.

    Render a font-based Bootstrap icon, for example::

        <i class="bi-star"></i>

    See the `Boostrap Icons <https://icons.getbootstrap.com/>`_ list for the
    list of icons.  Find an icon you like, and use the name of that icon on that
    page as the ``icon`` kwarg to the constructor, or set it as the :py:attr:`icon`
    class variable.

    Keyword Args:
        icon: the name of the icon to render, from the Bootstrap Icons list
        color: use this as Tabler color name to use as the foreground
            font color, leaving the background transparent.  If ``background``
            is also set, this is ignored.  Look at `Tabler: Colors
            <https://preview.tabler.io/docs/colors.html>`_
            for your choices; set this to the text after the ``bg-``
        background: use this as Tabler background/foreground color set for
            this icon.  : This overrides :py:attr:`color`. Look
            at `Tabler: Colors <https://preview.tabler.io/docs/colors.html>`_
            for your choices; set this to the text after the ``bg-``
    """

    tag: str = 'i'
    block: str = 'fonticon'

    #: The icon font family prefix.  One could override this to use FontAwesome icons,
    #: for instance, buy changing it to ``fa``
    prefix: str = 'bi'

    #: Use this as the name for the icon to render
    icon: Optional[str] = None
    #: If not ``None``, use this as Tabler color name to use as the foreground
    #: font color, leaving the background transparent.  If :py:attr:`background`
    #: is also set, this is ignored.  Look at `Tabler: Colors
    # <https://preview.tabler.io/docs/colors.html>`_  for your choices; set
    #: this to the text after the ``bg-``
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
        self.color = color if color else self.color
        self.background = background if background else self.background
        self.icon = icon if icon else self.icon
        if not self.icon:
            raise ValueError('"icon" is required as either a keyword argument or as a class attribute')
        self.icon = f'{self.prefix}-{icon}'
        if self._css_class is None:  # type: ignore
            self._css_class = ''
        self._css_class += f' {self.icon}'
        if self.color:
            self._css_class += f' text-{self.color} bg-transparent'
        elif self.background:
            self._css_class += f' bg-{self.background} text-{self.background}-fg'
