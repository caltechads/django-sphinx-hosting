from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import cast, Any, List, Dict, Optional
from urllib.parse import urlparse, unquote
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.functional import cached_property
from django.urls import reverse
from django_extensions.db.models import TimeStampedModel
from lxml import etree
import lxml.html
from lxml.html import HtmlElement
from wildewidgets.models import ViewSetMixin

from .fields import MachineNameField
from .settings import MAX_GLOBAL_TOC_TREE_DEPTH
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
    This is a :py:class:`dataclass` that we use with :py:class:`SphinxPageTree`
    to build out the global navigation structure for a set of documentation for
    a :py:class:`Version`.
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


@dataclass
class ClassifierNode:

    title: str
    classifier: Optional["Classifier"] = None
    items: Dict[str, "ClassifierNode"] = field(default_factory=dict)


# --------------------------
# Helper classes
# --------------------------

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

    def _traverse_level(self, pages, nodes):
        for node in nodes:
            if node.page:
                pages.append(node.page)
                if node.children:
                    self._traverse_level(pages, node.children)

    def traverse(self) -> List["SphinxPage"]:
        """
        Return a list of the pages represented in this tree.
        """
        pages: List["SphinxPage"] = [cast("SphinxPage", self.head.page)]
        self._traverse_level(pages, self.head.children)
        return pages


class SphinxPageTreeProcessor:

    def build_item(self, node: TreeNode) -> Dict[str, Any]:
        """
        Build a :py:class:`wildewdigets.MenuItem` compatible
        dict representing ``node``.

        Args:
            node: the current node in our page tree

        Returns:
            A dict suitable for loading into a :py:class:`wildewidgets.MenuItem`.
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
        Build a :py:class:`wildewdigets.MenuItem` compatible
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
            for li in html.iterchildren():
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
        for elem in html.iterchildren():
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
                {'text': 'bar', 'url': '/project/version/foo', 'icon': None}
                {'text': 'bar', 'url': '/project/version/bar', 'icon': None, items: [{'text': 'blah' ...} ...]}
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
                print(
                    etree.tostring(
                        html,
                        method='xml',
                        encoding='unicode',
                        pretty_print=True
                    )  # pylint: disable=c-extension-no-member
                )
            return self.parse_globaltoc(html)
        else:
            return []

# --------------------------
# FileField upload functions
# --------------------------


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

# --------------------------
# Managers
# --------------------------


class ClassifierManager(models.Manager):

    def tree(self) -> Dict[str, ClassifierNode]:
        """
        Given our classifiers, which are ``::`` separated lists of terms
        like::

            Section :: Subsection :: Name
            Section :: Subsection :: Name2
            Section :: Subsection :: Name3
            Section :: Subsection

        Return a tree-like data structure that looks like::

            {
                'Section': ClassifierNode(
                    title='Section'
                    items={
                        'Subsection': ClassifierNode(
                            title='Subsection',
                            classifier=Classifier(name="Section :: Subsection"),
                            items: {
                                'Name': ClassifierNode(
                                    title='Name',
                                    classifier=Classifier(
                                        name='Section :: Subsection :: Name'
                                    )
                                ),
                                ...
                            }
                        )
                    }
                )
            }
        """
        nodes: Dict[str, ClassifierNode] = {}
        current: Optional[ClassifierNode] = None
        for classifier in self.get_queryset().all():
            parts = classifier.name.split(' :: ')
            if parts[0] not in nodes:
                nodes[parts[0]] = ClassifierNode(title=parts[0])
            current = nodes[parts[0]]
            if len(parts) > 1:
                for part in parts[1:]:
                    if part not in current.items:
                        current.items[part] = ClassifierNode(title=part)
                    current = current.items[part]
            current.classifier = classifier
        return nodes


# --------------------------
# Models
# --------------------------


class Classifier(ViewSetMixin, models.Model):
    """
    A :py:class:`Project` can be tagged with one or more :py:class:`Classifier`
    tags.  This allows you to group projects by ecosystem, or type, for example.

    Use `PyPI <www.pypi.org>`_ classifiers as an example of how to use a single
    field for classifying across many dimensions.

    Examples::

        Ecosystem :: CMS
        Language :: Python
        Owner :: DevOps :: AWS
    """
    objects = ClassifierManager()

    name: F = models.CharField(
        'Classifier Name',
        help_text=_('The classifier spec for this classifier, e.g. "Language :: Python"'),
        max_length=255,
        unique=True,
    )

    def save(self, *args, **kwargs) -> None:
        """
        Overrides :py:meth:`django.db.models.Model.save`.

        Override save to create any missing classifiers in our chain.  For example,
        if we want to create this classifier::

            Foo :: Bar :: Baz

        But ``Foo :: Bar`` does not yet exist in the database, create that before
        creating ``Foo :: Bar :: Baz``.  We do this so that when we filter our projects
        by classifier, we can filter by ``Foo :: Bar`` and ``Foo :: Bar :: Baz``.
        """
        parts = [p.strip() for p in self.name.split('::')]
        if len(parts) > 2:
            name = parts[0]
            for part in parts[1:-1]:
                name = f'{name} :: {part}'
                if not self.objects.filter(name=name).exists():
                    new_classifiier = Classifier(name=name)
                    new_classifiier.save(using=kwargs.get('using', settings.DEFAULT_DB_ALIAS))
        # Rejoin our parts to ensure we always get a classifier that looks like
        # "part :: part :: part" instead of "part:: part::part"
        self.name = ' :: '.join(parts)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return str(self.name)

    class Meta:
        verbose_name = _('classifier')
        verbose_name_plural = _('classifiers')


class ProjectPermissionGroup(
    ViewSetMixin,
    TimeStampedModel,
    models.Model
):
    """
    A :py:class:`Project` can be assigned to one or more
    :py:class:`ProjectPermissionGroup` groups.  This restricts viewing of the
    project to users which belong to those groups.

    Examples::

        Ecosystem :: CMS
        Language :: Python
        Owner :: DevOps :: AWS
    """
    name: F = models.CharField(
        'Permission Group Name',
        help_text=_('The name for this permission group'),
        max_length=100,
        unique=True,
    )
    description: F = models.CharField(
        'Brief Description',
        max_length=256,
        null=True,
        blank=True,
        help_text=_('A brief description of this permission group'),
        validators=[NoHTMLValidator()]
    )

    users: M2M = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='project_permission_groups'
    )

    class Meta:
        verbose_name = _('project permission group')
        verbose_name_plural = _('project permission groups')


class Project(ViewSetMixin, TimeStampedModel, models.Model):
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
    machine_name: F = MachineNameField(
        'Machine Name',
        unique=True,
        help_text=_(
            """Must be unique.  Set this to the slugified value of "project" in Sphinx's. conf.py"""
        )
    )

    permission_groups: M2M = models.ManyToManyField(
        ProjectPermissionGroup,
        related_name='projects',
    )
    classifiers: M2M = models.ManyToManyField(
        Classifier,
        related_name='projects',
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
        return reverse('sphinx_hosting:project--detail', args=[self.machine_name])

    def get_update_url(self) -> str:
        return reverse('sphinx_hosting:project--update', args=[self.machine_name])

    def get_latest_version_url(self) -> Optional[str]:
        if self.latest_version:
            return reverse(
                'sphinx_hosting:sphinxpage--detail',
                args=[
                    self.machine_name,
                    self.latest_version.version,
                    self.latest_version.head.relative_path
                ]
            )
        return None

    class Meta:
        verbose_name = _('project')
        verbose_name_plural = _('projects')


class Version(TimeStampedModel, models.Model):
    """
    A ``Version`` is a specific version of a :py:class:`Project`.  Versions own
    :py:class:`SphinxPage` objects.
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
    archived: F = models.BooleanField(
        'Archived?',
        default=False,
        help_text=_(
            'Whether this version should be excluded from search indexes'
        )
    )

    head: FK = models.OneToOneField(
        "SphinxPage",
        on_delete=models.SET_NULL,
        null=True,
        related_name='+',  # disable our related_name for this one
        help_text=_('The top page of the documentation set for this version of our project'),
    )

    def __str__(self) -> str:
        return f'{self.project.title}-{self.version}'

    @property
    def is_latest(self) -> bool:
        return self == self.project.latest_version

    @property
    def page_tree(self) -> SphinxPageTree:
        """
        Return the page hierarchy for the set of :py:class:`SphinxPage` pages in
        this version.

        The page hierarchy is build by traversing the pages in the set, starting
        with :py:attr:`head`.

        Returns:
            The page hierarchy for this version.
        """
        return SphinxPageTree(self)

    def mark_searchable_pages(self) -> None:
        """
        Set the :py:attr:`SphinxPage.searchable` flag on
        the searchable pages in this version.

        Searchable pages are ones that:

        * Are not in :py:attr:`SphinxPage.SPECIAL_PAGES`
        * Do not have a part of their relative path that starts with ``_``.

        Go through the pages in this version, and set
        :py:attr:`SphinxPage.searchable` to ``True`` for all those which meet the above
        requirements, ``False`` otherwise.
        """
        ignored_paths = list(SphinxPage.SPECIAL_PAGES.keys())
        for page in self.pages.all():
            if (
                page.relative_path not in ignored_paths and
                not page.relative_path.startswith('_') and
                '/_' not in page.relative_path
            ):
                page.searchable = True
            else:
                page.searchable = False
            page.save()

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
        :py:class:`sphinx_hosting.wildewidgets.SphinxPageGlobalTableOfContentsMenu`
        for this :py:class:`Version`.

        """
        items = SphinxGlobalTOCHTMLProcessor(max_level=MAX_GLOBAL_TOC_TREE_DEPTH).run(self)
        if not items:
            items = SphinxPageTreeProcessor().run(self)
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
    #: json data, but ``title`` is required for pages
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
        'Body (Original)',
        blank=True,
        help_text=_(
            'The original body for the page, extracted from the page JSON. Some pages have no body. '
            'We save this here in case we need to reprocess the body at some later date.'
        ),
    )
    body: F = models.TextField(
        'Body',
        blank=True,
        help_text=_(
            'The body for the page, extracted from the page JSON, and modified to suit us.  '
            'Some pages have no body.  The body is actually stored as a Django template.'
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
    searchable: F = models.BooleanField(
        'Searchable',
        default=False,
        help_text=_('Should this page be included in the search index?')
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
        return f'{self.version.project.title}-{self.version.version}: {self.relative_path}'

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
