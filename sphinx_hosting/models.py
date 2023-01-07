from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Any, List, Dict, Optional, TYPE_CHECKING
from urllib.parse import urlparse, unquote

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.functional import cached_property
from django.urls import reverse
from django_extensions.db.models import TimeStampedModel
from lxml import etree
import lxml.html
from lxml.html import HtmlElement

from .validators import NoHTMLValidator


F = models.Field
M2M = models.ManyToManyField
FK = models.ForeignKey


# --------------------------
# Dataclasses
# --------------------------

@dataclass
class TreeNode:
    """
    This is a dataclass that we use with :py:class:`SphinxTree` to build out the
    global navigation structure for a set of documentation for a
    :py:class:`Version`.
    """

    #: The page title
    title: str
    #: This page
    page: Optional["SphinxPage"] = None
    #: The :py:class:`SphinxPage` after this one
    prev: Optional["SphinxPage"] = None
    #: The :py:class:`SphinxPage` before this one
    next: Optional["SphinxPage"] = None
    #: The :py:class:`SphinxPage` that is this page's parent
    parent: Optional["SphinxPage"] = None
    #: The :py:class:`TreeNode` objects that are this page's children
    children: List["TreeNode"] = field(default_factory=list)

    @classmethod
    def from_page(cls, page: "SphinxPage") -> "TreeNode":
        """
        Build a :py:class:`TreeNode` from ``page``.

        Note:
            This does not populate :py:attr:`children`; :py:class:`SphinxPageTree`
            will populate it as appropriate as it ingests pages.

        Args:
            page: the :py:class:`SphinxPage` from which to build a node

        Returns:
            A configured node.
        """
        return cls(
            page=page,
            title=page.title,
            next=page.next_page,
            prev=page.previous_page.first(),
            parent=page.parent
        )


class SphinxPageTree:
    """
    A class that holds the page hierarchy for the set of :py:class:`SphinxPage`
    pages in a :py:class:`Version`.as a linked set of :py:class:`TreeNode`
    objects.

    The page heirarchy is built by starting at :py:attr:`Version.head` and
    following the page linkages by looking at :py:attr:`SphinxPage.next_page`,
    stopping the traversal when we find a :py:attr:`SphinxPage.next_page` that is ``None``.

    As we traverse, if a :py:attr:`SphinxPage.parent` is not ``None``, find the
    :py:class:`TreeNode` for that parent, and add the page to
    :py:attr:`TreeNode.children`.

    For pages who have no :py:attr:`SpinxPage.parent`, assume they are top level
    children of the set, and make them children of :py:class:`Version.head`.

    Load it like so::

        >>> project = Project.objects.get(machine_name='my-project')
        >>> version = project.versions.get(version='1.0.0')
        >>> tree = SphinxPageTree(version)

    You can then traverse the built hierarchy by starting at
    :py:attr:`SphinxPageTree.head`, looking at its children, then looking at
    their children, etc..

        >>>

    """

    def __init__(self, version: "Version"):
        #: The :py:class:`Version that this tree examines
        self.version: Version = version
        self.nodes: Dict[int, TreeNode] = {}
        self.nodes[self.version.head.id] = TreeNode.from_page(self.version.head)
        #: The top page in the page hierarchy
        self.head: TreeNode = self.nodes[self.version.head.id]
        self.build(version)

    def build(self, version: "Version"):
        self.add_page(version.head)

    def add_page(self, page: "SphinxPage"):
        node = TreeNode.from_page(page)
        self.nodes[page.id] = node
        if node.parent:
            if node.parent.id in self.nodes:
                self.nodes[node.parent.id].children.append(node)
        else:
            # The top level pages that are not head will not have any parent
            # because Sphinx doesn't think that way
            if node != self.head:
                self.head.children.append(node)
        if node.next:
            self.add_page(node.next)


class SphinxPageTreeProcesor:

    def build_item(self, node: TreeNode) -> Dict[str, Any]:
        """
        Build a :py:class:`sphinx_hosting.wildewdigets.MenuItem` compatible
        dict representing ``node``.

        Args:
            node: the current node in our page tree

        Returns:
            A dict suitable for loading into a ``MenuItem``
        """
        item: Dict[str, Any] = {
            'text': node.title,
            'url': None,
            'icon': None,
            'items': []
        }
        if node.page:
            item['url'] = node.page.get_absolute_url()
        return item

    def build(self, items: List[Dict[str, Any]], node: TreeNode) -> None:
        """
        Build a :py:class:`sphinx_hosting.wildewdigets.MenuItem` compatible
        dict representing ``node``, and append it to ``items``.

        if ``node`` has children, recurse into those children, building out
        our submenus.

        Args:
            items: the current list of ``MenuItem`` compatible dicts for the
                current level of the menu
            node: the current node in our page tree
        """
        item = self.build_item(node)
        if node.children:
            for child in node.children:
                self.build(item['items'], child)
        items.append(item)

    def run(self, version: "Version") -> List[Dict[str, Any]]:
        """
        Parse the :py:func:`Version.page_tree` and return a struct that looks like:
        with
        :py:class:`sphinx_hosting.wildewidgets.SphinxPageGlobalTableOfContentsMenu.parse_obj`

        The returned struct should look something like this::

            [
                {'text': 'foo'},
                {'text': 'bar', 'url': '/foo', 'icon': None}
                {'text': 'bar', 'url': '/foo', 'icon': None, items: [{'text': 'blah' ...} ...]}
                ...
            ]

        Args:
            version: the version whose global table of contents we are parsing

        Returns:
            A list of dicts representing the global menu structure
        """
        self.sphinx_tree = version.page_tree
        items: List[Dict[str, Any]] = []
        items.append(self.build_item(self.sphinx_tree.head))
        for child in self.sphinx_tree.head.children:
            self.build(items, child)
        return items


class SphinxGlobalTOCHTMLProcessor:
    """
    **Usage**: ``SphinxGlobalTOCHTMLProcessor().run(version, globaltoc_html)```

    This importer is used to parse the ``globaltoc`` key in JSON output of
    Sphinx pages built with the `sphinxcontrib-jsonglobaltoc
    <https://github.com/caltechads/sphinxcontrib-jsonglobaltoc>`_ extension.

    Sphinx uses your ``.. toctree:`` declarations in your ``.rst`` files to
    build site navigation for your document tree, and
    ``sphinxcontrib-jsonglobaltoc`` saves the Sphinx HTML produced by those
    ``..toctree`` as the ``globaltoc`` key in the `.fjson` output.

    Note:

        Sphinx ``.. toctree:`` are ad-hoc -- they're up to how the author wants
        to organize their content, and may not reflect how files are filled out
        in the filesystem.
    """

    def __init__(self, max_level: int = 2) -> None:
        #: Generate at most this many levels of menus and submenus
        self.max_level: int = max_level

    def fix_href(self, href: str) -> str:
        p = urlparse(unquote(href))
        url = reverse(
            'sphinx_hosting:sphinxpage--detail',
            kwargs={
                'project_slug': self.version.project.machine_name,
                'version': self.version.version,
                'path': p.path.strip('/')
            }
        )
        if p.fragment:
            url += f'#{p.fragment}'
        return url

    def parse_ul(self, html: HtmlElement, level: int = 1) -> List[Dict[str, Any]]:
        """
        Process ``html``, an ``lxml`` parsed set of elements representing the contents
        of a ``<ul>`` from a Sphinx table of contents and return a list of
        :py:class:`sphinx_hosting.wildewidgets.MenuItem` objects.

        Any ``href`` in links found will be converted to its full
        ``django-sphinx-hosting`` path.

        If we find another ``<ul>`` inside ``html``, process it by passing its
        contents to :py:meth:`parse_ul` again, incrementing the menu level.

        If ``level`` is greater than :py:attr:`max_level`, return an empty list,
        stopping our recursion.

        Args:
            html: the list of elements that are the contents of the parent ``<ul>``

        Keyword Args:
            level: the current menu level

        Returns:
            The ``<ul>`` contents as a list of dicts
        """
        items: List[Dict[str, Any]] = []
        if level <= self.max_level:
            for li in html:
                item: Dict[str, Any] = {
                    'text': 'placeholder',
                    'url': None,
                    'icon': None,
                    'items': []
                }
                for elem in li:
                    if elem.tag == 'a':
                        item['text'] = elem.text_content()
                        item['url'] = self.fix_href(elem.attrib['href'])
                    if elem.tag == 'ul':
                        item['items'].extend(self.parse_ul(elem, level=level + 1))
                items.append(item)
        return items

    def parse_globaltoc(self, html: HtmlElement) -> List[Dict[str, Any]]:
        """
        Parse our global table of contents HTML blob and return a list of
        :py:class:`sphinx_hosting.wildewidgets.MenuItem` objects.

        How our mapping works:

        * Multiple top level ``<ul>`` tags separated by ``<p class="caption">`` tags will be
          merged into a single list.
        * ``<p class="caption ...">CONTENTS</p>`` becomes ``{'text': 'CONTENTS'}```
        * Any ``href`` will be converted to its full ``django-sphinx-hosting`` path

        Args:
            version: the version whose global table of contents we are parsing
            html: the lxml parsed HTML of the global table of contents from Sphinx
        """
        items: List[Dict[str, Any]] = []
        for elem in html:
            if elem.tag == 'p' and 'caption' in elem.classes:
                # Captions only appear at the top level, even if you assign
                # captions in your toctree declaration in your sub levels with
                # :caption:, so we only process them here.
                items.append({'text': elem.text_content()})
            if elem.tag == 'ul':
                items.extend(self.parse_ul(elem))
        return items

    def run(
        self,
        version: "Version",
        verbose: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Parse the global table of contents found as
        ``version.head.orig_global_toc`` into a data struct suitable for use
        with
        :py:class:`sphinx_hosting.wildewidgets.SphinxPageGlobalTableOfContentsMenu.parse_obj`
        and return it.

        How our mapping works:

        * Multiple top level ``<ul>`` tags separated by ``<p class="caption">``
          tags will be merged into a single list.
        * ``<p class="caption ...">CONTENTS</p>`` becomes ``{'text': 'CONTENTS'}```
        * Any ``href`` for links found will be converted to its full
          ``django-sphinx-hosting`` path

        The returned struct should look something like this::

            [
                {'text': 'foo'},
                {'text': 'bar', 'url': '/foo', 'icon': None}
                {'text': 'bar', 'url': '/foo', 'icon': None, items: [{'text': 'blah' ...} ...]}
                ...
            ]

        Args:
            version: the version whose global table of contents we are parsing

        Keyword Args:
            verbose: if ``True``, pretty print the HTML of the globaltoc

        Returns:
            A list of dicts representing the global menu structure
        """
        self.version = version
        # This is really only necessary to get the pretty printer below to
        # work properly.  If the \n chars are not removed, lxml won't indent
        # properly
        if self.version.head.orig_global_toc:
            global_toc_html = re.sub(r'\n', '', self.version.head.orig_global_toc)
            html = lxml.html.fromstring(global_toc_html)
            if verbose:
                print(etree.tostring(html, method='xml', encoding='unicode', pretty_print=True))
            return self.parse_globaltoc(html)
        else:
            return []


def sphinx_image_upload_to(instance: "SphinxImage", filename: str) -> str:
    """
    Set the upload path within our ``MEDIA_ROOT`` for any images used by our Sphinx
    documentation to be::

        {project machine_name}/{version}/images/{image basename}

    Args:
        instance: the :py:class:`SphinxImage` object
        filename: the original path to the file

    Returns:
        The properly formatted path to the file
    """
    path = Path(instance.version.project.machine_name) / Path(instance.version.version) / 'images'
    path = path / Path(filename).name
    return str(path)


class Project(TimeStampedModel, models.Model):
    """
    A Project is what a set of Sphinx docs describes: an application, a library, etc.

    Projects have versions (:py:class:`Version`) and versions have Sphinx pages
    (:py:class:`SphinxPage`).
    """

    title: F = models.CharField(
        'Project Name',
        help_text=_('The human name for this project'),
        max_length=100
    )
    description: F = models.CharField(
        'Brief Description',
        max_length=256,
        null=True,
        blank=True,
        help_text=_('A brief description of this project'),
        validators=[NoHTMLValidator()]
    )
    machine_name: F = models.SlugField(
        'Machine Name',
        unique=True,
        help_text=_("""Must be unique.  Set this to the value of "project" in Sphinx's. conf.py""")
    )

    def __str__(self) -> str:  # pylint: disable=invalid-str-returned
        return self.title

    @property
    def latest_version(self) -> "Optional[Version]":
        """
        Return the latest version (by version number) of our project
        documentation, if any.

        Returns:
            The latest version of our project.
        """
        return self.versions.order_by('-version').first()

    def get_absolute_url(self) -> str:
        return reverse('sphinx_hosting:project--update', args=[self.machine_name])

    class Meta:
        verbose_name: str = _('project')
        verbose_name_plural: str = _('projects')


class Version(TimeStampedModel, models.Model):
    """
    A Version is a specific version of a :py:class:`Project`.  Versions own
    Sphinx pages (:py:class:`SphinxPage`)
    """

    project: FK = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='versions',
        help_text=_('The Project to which this Version belongs'),
    )
    version: F = models.CharField(
        'Version',
        max_length=64,
        null=False,
        help_text=_('The version number for this release of the Project'),
    )

    sphinx_version: F = models.CharField(
        'Sphinx Version',
        max_length=64,
        null=True,
        blank=True,
        default=None,
        help_text=_('The version of Sphinx used to create this documentation set')
    )

    head: FK = models.OneToOneField(
        "SphinxPage",
        on_delete=models.SET_NULL,
        null=True,
        related_name='+',  # disable our related_name for this one
        help_text=_('The top page of the documentation set for this version of our project'),
    )

    @property
    def page_tree(self) -> SphinxPageTree:
        """
        Return the page hierarchy for the set of :py:class:`SphinxPage` pages in
        this version.  This is a :py:func:`cached_property`; it will be calculated
        only once and then cached.

        The page hierarchy is build by traversing the pages in the set, starting
        with :py:attr:`head`.

        Returns:
            The page hierarchy for this version.
        """
        return SphinxPageTree(self)

    @cached_property
    def globaltoc(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Build a struct that looks like this::

            {
                items: [
                    {'text': 'foo'},
                    {'text': 'bar', 'url': '/foo', 'icon': None}
                    {'text': 'bar', 'url': '/foo', 'icon': None, items: [{'text': 'blah' ...} ...]}
                    ...
                ]
            }

        suitable for constructing a
        :py:class:`sphinx_hosting.wildewdigets.SphinxPageGlobalTableOfContentsMenu`
        for this :py:class:`Version`.

        """
        items = SphinxGlobalTOCHTMLProcessor().run(self)
        if not items:
            items = SphinxPageTreeProcesor().run(self)
        return {'items': items}

    def purge_cached_globaltoc(self) -> None:
        """
        Purge the cached output from our :py:meth:`globaltoc` property.
        """
        try:
            del self.globaltoc
        except AttributeError:
            # This means self.globaltoc hasn't been accessed yet
            pass

    def get_absolute_url(self) -> str:
        return reverse(
            'sphinx_hosting:version--detail',
            args=[self.project.machine_name, self.version]
        )

    def save(self, *args, **kwargs):
        """
        Overriding :py:meth:`django.db.models.Model.save` here so that we can
        purge our cached global table of contents.
        """
        super().save(*args, **kwargs)
        self.purge_cached_globaltoc()


class SphinxPage(TimeStampedModel, models.Model):
    """
    A ``SphinxPage`` is a single page of a set of Sphinx documentation.
    ``SphinxPage`` objects are owned :py:class:`Version` objects, which are in
    turn owned by :py:class:`Project` objects.
    """

    #: This is a mapping between filename and title that identifies the
    #: special pages that Sphinx produces on its own and gives them
    #: reasonable titles.  These pages have no ``title`` key in their
    #: json data
    SPECIAL_PAGES: Dict[str, str] = {
        'genindex': 'General Index',
        'py-modindex': 'Module Index',
        'np-modindex': 'Module Index',
        'search': 'Search',
        '_modules/index': 'Module code'
    }

    version: FK = models.ForeignKey(
        Version,
        on_delete=models.CASCADE,
        related_name='pages',
        help_text=_('The Version to which this page belongs'),
    )
    relative_path: F = models.CharField(
        'Relative page path',
        help_text=_('The path to the page under our top slug'),
        max_length=255
    )
    content: F = models.TextField(
        'Content',
        help_text=_('The full JSON payload for the page')
    )
    title: F = models.CharField(
        'Title',
        max_length=255,
        help_text=_('Just the title for the page, extracted from the page JSON')
    )
    orig_body: F = models.TextField(
        'Body (Original',
        blank=True,
        help_text=_(
            'The original body for the page, extracted from the page JSON. Some pages have no body.'
            'We save this here in case we need to reprocess the body at some later date.'
        ),
    )
    body: F = models.TextField(
        'Body',
        blank=True,
        help_text=_(
            'The body for the page, extracted from the page JSON, and modified to suit us.  '
            'Some pages have no body.'
        ),
    )
    orig_local_toc: F = models.TextField(
        'Local Table of Contents (original)',
        blank=True,
        null=True,
        default=None,
        help_text=_(
            'The original table of contents for headings in this page.'
            'We save this here in case we need to reprocess the table of contents '
            'at some later date.'
        ),
    )
    local_toc: F = models.TextField(
        'Local Table of Contents',
        blank=True,
        null=True,
        default=None,
        help_text=_('Table of Contents for headings in this page, modified to work in our templates'),
    )

    orig_global_toc: F = models.TextField(
        'Global Table of Contents (original)',
        blank=True,
        null=True,
        default=None,
        help_text=_(
            'The original global table of contents HTML attached to this page, if any.  This '
            'will only be present if you had "sphinxcontrib-jsonglobaltoc" installed in your "extensions" '
            'in the Sphinx conf.py'
        ),
    )

    parent: FK = models.ForeignKey(
        "SphinxPage",
        on_delete=models.CASCADE,
        null=True,
        related_name="children",
        help_text=_('The parent page of this page'),
    )

    # This has to be a ForeignKey here and not a OneToOneField becuase
    # more than one page can have the same next_page.
    next_page: FK = models.ForeignKey(
        "SphinxPage",
        on_delete=models.CASCADE,
        null=True,
        related_name="previous_page",
        help_text=_('The next page in the documentation set'),
    )

    def __str__(self) -> str:  # pylint: disable=invalid-str-returned
        return self.relative_path

    def get_absolute_url(self) -> str:
        return reverse(
            'sphinx_hosting:sphinxpage--detail',
            args=[
                self.version.project.machine_name,
                self.version.version,
                self.relative_path
            ]
        )

    class Meta:
        verbose_name = _('sphinx page')
        verbose_name_plural = _('sphinx pages')
        unique_together = ('version', 'relative_path')


class SphinxImage(TimeStampedModel, models.Model):
    """
    A ``SphinxImage`` is an image file referenced in a Sphinx document.  When
    importing documenation packages, we extract all images from the package,
    upload them into Django storage and update the Sphinx HTML in
    :py:attr:`SphinxPage.body` to reference the URL for the uploaded image
    instead of its original url.
    """

    version: FK = models.ForeignKey(
        Version,
        on_delete=models.CASCADE,
        related_name='images',
        help_text=_('The version of our project documentation with which this image is associated')
    )
    orig_path: F = models.CharField(
        _('Original Path'),
        max_length=256,
        help_text=_('The original path to this file in the Sphinx documentation package')
    )
    file: F = models.FileField(
        _('An image file'),
        upload_to=sphinx_image_upload_to,
        help_text=_('The actual image file')
    )

    class Meta:
        verbose_name = _('sphinx image')
        verbose_name_plural = _('sphinx images')
        unique_together = ('version', 'orig_path')
