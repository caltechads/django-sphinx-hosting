from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple, Union, cast

from wildewidgets import Block


DatagridItemDef = Union["DatagridItem", Tuple[str, str], Tuple[str, str, Dict[str, Any]]]


class DatagridItem(Block):
    """
    Extends :py:class:`wildewidgets.Block`.

    This widget implements a `Tabler datagrid-item
    <https://preview.tabler.io/docs/datagrid.html`_ It should be used with
    :py:class:`Datagrid`.

    Keyword Args:
        title: the ``datagrid-title`` of the ``datagrid-item``
        content: the ``datagrid-content`` of the ``datagrid-item``
        url: URL to use to turn content into a hyperlink

    Raises:
        ValueError: either the ``title`` or the ``content`` was empty
    """
    block: str = 'datagrid-item'

    title: Optional[str] = None  #: the ``datagrid-title`` of the ``datagrid-item``
    content: Optional[Union[str, Block]] = None  #: the ``datagrid-content`` of the ``datagrid-item``
    url: Optional[str] = None  #: a URL to use to turn content into a hyperlink

    def __init__(
        self,
        title: str = None,
        content: Union[str, Block] = None,
        url: str = None,
        **kwargs
    ) -> None:
        self.title = title if title else self.title
        if not self.title:
            raise ValueError('"title" is required as either a keyword argument or as a class attribute')
        self.content = content if content else deepcopy(self.content)
        if not self.content:
            raise ValueError('"content" is required as either a keyword argument or as a class attribute')
        self.url = url if url else self.url
        super().__init__(**kwargs)
        if self.url:
            wrapper: Block = Block(
                self.content,
                tag='a',
                attributes={'href': self.url},
                name='datagrid-conetnt'
            )
        else:
            if not isinstance(self.content, Block):
                # Wrap the text in a block to allow us to assign the datagrid-content
                # class to it
                wrapper = Block(self.content, name='datagrid-content')
            else:
                wrapper = self.content
        self.add_block(Block(self.title, name='datagrid-title'))
        self.add_block(wrapper)


class Datagrid(Block):
    """
    Extends :py:class:`wildewidgets.Block`.

    This widget implements a `Tabler Data grid <https://preview.tabler.io/docs/datagrid.html`_
    It contains :py:class:`DatagridItem` objects.

    Add :py:class:`DatagridItem` objects to this in one of these ways:

    As constructor arguments::

        >>> item1 = DatagridItem(title='foo', content='bar', url="https://example.com")
        >>> item2 = DatagridItem(title='baz', content='barney')
        >>> item3 = ['foo', 'bar']
        >>> grid = Datagrid(item1, item2, item3)

    By using :py:meth:`add_block` with a :py:class:`DatagridItem`:

        >>> grid = Datagrid(item1, item2, item3)
        >>> grid.add_block(DatagridItem(title='foo', content='bar'))

    By using :py:meth:`add_item`::

        >>> grid = Datagrid(item1, item2, item3)
        >>> grid.add_item('foo', 'bar')

    Args:
        *items: a list of ``datagrid-item`` definitions or :py:class:`DatagridItem` objects.
    """
    block: str = 'datagrid'
    items: List[DatagridItemDef] = []  #: a list of ``datagrid-items`` to add to our content

    def __init__(self, *items: DatagridItemDef, **kwargs):
        self.items = list(items) if items else deepcopy(self.items)
        super().__init__(**kwargs)
        for item in items:
            if isinstance(item, DatagridItem):
                self.add_block(item)
            elif isinstance(item, tuple):
                if len(item) == 2:
                    item = cast(Tuple[str, str], item)
                    self.add_item(item[0], item[1])
                else:
                    item = cast(Tuple[str, str, Dict[str, Any]], item)
                    self.add_item(item[0], item[1], **item[2])

    def add_item(self, title: str, content: str, url: str = None, **kwargs) -> None:
        """
        Add a :py:class:`DatagridItem` to our block contents, with
        ``datagrid-title`` of ``title`` and datagrid

        Keyword Args:
            title: the ``datagrid-title`` of the ``datagrid-item``
            content: the ``datagrid-content`` of the ``datagrid-item``
            url: URL to use to turn content into a hyperlink
        """
        self.add_block(DatagridItem(title=title, content=content, url=url, **kwargs))
