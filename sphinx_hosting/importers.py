import fnmatch
import io
import json
import re
import tarfile
import urllib.parse
from dataclasses import dataclass
from pathlib import Path
from typing import IO, Any, Dict, Final, List, Optional, TypeAlias, cast  # noqa: UP035

import lxml.html
import semver
from django.utils.text import slugify
from lxml.etree import XML  #: pylint: disable=no-name-in-module

from .exc import VersionAlreadyExists
from .logging import logger
from .models import Project, SphinxDocument, SphinxImage, SphinxPage, Version
from .search_indexes import SphinxPageIndex
from .settings import EXCLUDE_FROM_LATEST

ImageMap: TypeAlias = Dict[str, SphinxImage]
DocumentMap: TypeAlias = Dict[str, SphinxDocument]


@dataclass
class PageTreeNode:
    """
    A data structure to temporarily hold relationships between
    :py:class:`sphinx_hosting.models.SphinxPage` objects while importing pages.

    In the page JSON we get from Sphinx, we only know the titles of related
    pages, so we store them here along with the
    :py:class:`sphinx_hosting.models.SphinxPage` we created from our JSON, and
    then do another pass through these :py:class:`PageTreeNode` objects to link
    our pages together.

    This is used in :py:meth:`SphinxPackageImporter.link_pages`.
    """

    #: The page for this node
    page: SphinxPage
    #: The title of the parent page for this node, if any
    parent_title: Optional[str] = None  # noqa: FA100
    #: The title of the next page for this node, if any
    next_title: Optional[str] = None  # noqa: FA100


class SphinxPackageImporter:
    """
    **Usage**: ``SphinxPackageImporter().run(sphinx_tarfilename)```

    Import a tarfile of a built set of Sphinx documentation into the database.

    .. important::

        Before importing, there must be a
        :py:class:`sphinx_hosting.models.Project` in the database whose
        ``machine_name`` matches the ``project`` in Sphinx's ``conf.py`` config
        file for the docs to be imported.

    The documentation package should have been built via the ``json`` output from
    ``sphinx-build``, so either:

    .. code-block:: bash

        make json

    or:

    .. code-block:: bash

        sphinx-build -n -b json build/json

    The tarfile should be built like so:

    .. code-block:: bash

        cd build
        tar zcf mydocs.tar.gz json

    ensuring that the package contents are enclosed in a folder.

    When run, :py:class:`SphinxPackageImporter` will look inside the tarfile at
    the ``globalcontext.json`` file to determine which project and version we should
    associate these pages with.

    * The ``project`` key in will be used to look up the
      :py:class:`sphinx_hosting.models.Project` to associate these Sphinx pages
      with, using ``project`` as :py:attr:`sphinx_hosting.models.Project.machine_name`
    * The ``version`` key will be used to create a new
      :py:class:`sphinx_hosting.models.Version` object tied to that project

    Once the :py:class:`sphinx_hosting.models.Version` has been created, the
    pages in the tarfile will be created as
    :py:class:`sphinx_hosting.models.SphinxPage` objects, and the images will be
    created as :py:class:`sphinx_hosting.models.SphinxImage` objects.
    """

    # Sometimes pages have weird titles -- replace them with their filename
    ODD_TITLES: Final[List[str]] = ["&lt;no title&gt;"]

    def __init__(self) -> None:
        #: Used to map original Sphinx image paths to our Django storage path
        self.image_map: ImageMap = {}
        #: Used to map original Sphinx document paths to our Django storage path
        self.document_map: DocumentMap = {}
        #: Used to link pages to their parent pages, and to their next pages
        self.page_tree: Dict[str, PageTreeNode] = {}
        self.name_map: Dict[str, str] = {}
        #: the contents of globalcontext.json
        self.config: Dict[str, Any] = {}

    def _get_file(self, package: tarfile.TarFile, filename: str) -> io.BufferedReader:
        """
        Look through the member names in our tarfile ``package`` for
        ``filename``, and return an open file descriptor on that file.

        Note:
          We have to do it this way instead of using ``package.getmember(name)``
          because we don't know the name of the containing folder.

        Args:
            package: the opened Sphinx documentation tarfile
            filename: the name of the file we're looking for

        Raises:
            KeyError: no file named ``filename`` was found in the tarfile

        Returns:
            The opened file descriptor for our file.

        """
        if not self.name_map:
            self.name_map = {
                str(Path(*Path(name).parts[1:])): name for name in package.getnames()
            }
        if filename not in self.name_map:
            msg = f'Sphinx docs TarFile has no file named "{filename}"'
            raise KeyError(msg)
        return cast(io.BufferedReader, package.extractfile(self.name_map[filename]))

    def _update_image_src(self, body: str) -> str:
        """
        Given an HTML body of a Sphinx page, update the ``<img src="path">``
        references to template tag expressions that load the actual image URL
        from the :py:class:`sphinx_hosting.models.SphinxImage` objects at render time.

        We need to defer filling in the URL of the image until render time
        because of things like storing images in S3 and using time-limited S3
        auth parameters to retrieve the image from a private bucket.  Those
        parameters expire typically after an hour, so if we don't defer figuring
        out the URL for our images, we end up storing a stale URL.

        Also deal with any lightboxes by converting them to the appropriate form
        to work with Tabler lightboxes.

        Args:
            body: the HTML body of a Sphinx document

        Returns:
            ``body`` with its ``<img>`` urls and lightbox attributes updated

        """
        if not body:
            return ""
        html = lxml.html.fromstring(body)
        images = html.cssselect("img")
        for image in images:
            # The image path is relative to the Sphinx page itself, so we need to
            # remove any "../" from the path so we can match the remainder to
            # our image_map
            src = re.sub(r"(\.\./)+", "", image.attrib["src"])
            if src in self.image_map:
                image.attrib["src"] = (
                    f"{{% sphinximage_url {self.image_map[src].id} %}}"
                )

        # also deal with any lightbox <a>
        lightboxes = html.cssselect("a[data-lightbox]")
        for lightbox in lightboxes:
            lightbox.attrib["data-fslightbox"] = lightbox.attrib["data-lightbox"]
            del lightbox.attrib["data-lightbox"]
            if "data-title" in lightbox.attrib:
                lightbox.attrib["data-caption"] = lightbox.attrib["data-title"]
                del lightbox.attrib["data-title"]
            src = re.sub(r"\.\./", "", lightbox.attrib["href"])
            if src in self.image_map:
                lightbox.attrib["href"] = (
                    f"{{% sphinximage_url {self.image_map[src].id} %}}"
                )
        return lxml.html.tostring(html).decode("utf-8")

    def _update_document_href(self, body: str) -> str:
        """
        Given an HTML body of a Sphinx page, update the ``<a class="reference
        download internal download="" href="__the_orig_path__">`` references to
        template tag expressions that load the actual document URL from the
        :py:class:`sphinx_hosting.models.SphinxDocument` objects at render time.

        We need to defer filling in the href of the document until render time
        because of things like storing documents in S3 and using time-limited S3
        auth parameters to retrieve the image from a private bucket.  Those
        parameters expire typically after an hour, so if we don't defer figuring
        out the URL for our documents, we end up storing a stale URL.

        Args:
            body: the HTML body of a Sphinx document

        Returns:
            ``body`` with its ``<a>`` hrefs updated

        """
        if not body:
            return ""
        html = lxml.html.fromstring(body)
        docs = html.cssselect("a.download")
        for doc in docs:
            # The document path is relative to the Sphinx page itself, so we need to
            # remove any "../" from the path so we can match the remainder to
            # our image_map
            src = re.sub(r"(\.\./)+", "", doc.attrib["href"])
            if src in self.document_map:
                doc.attrib["href"] = (
                    f"{{% sphinxdocument_url {self.document_map[src].id} %}}"
                )
        return lxml.html.tostring(html).decode("utf-8")

    def load_config(self, package: tarfile.TarFile) -> None:
        """
        Load the ``globalcontext.json`` file for later reference.

        Args:
            package: the opened Sphinx documentation tarfile

        """
        self.config = json.loads(self._get_file(package, "globalcontext.json").read())

    def get_version(self, force: bool = False) -> Version:
        """
        Look in ``package`` for a member named ``globalcontext.json``, and load
        that file as JSON.

        Extract these things from that JSON:

            * the version string from the ``release`` key.
            * the ``machine_name`` of the :py:class:`Project` for this
              documentation tarfile as the slugified version of the ``project``
              key

        Return a new :py:class:`Version` instance on the project.

        Keyword Args:
            force: if ``True``, re-use an existing version, purging any docs and
              images associated with it first

        Raises:
            Project.DoesNotExist: no :py:class:`Project` exists whose
                ``machine_name`` matches the slugified ``project`` setting
                in the Sphinx package's ``conf.py``
            VersionAlreadyExists: a :py:class:`Version` with version string
                ``release`` from the Sphinx ``conf.py`` already exists for our
                project, and ``force`` was not ``True``

        """
        machine_name = self.config["project"]
        project = Project.objects.get(machine_name=machine_name)
        v = project.versions.filter(version=self.config["release"]).first()
        if v:
            if not force:
                msg = (
                    f"""Version {self.config['release']} of Project(machine_name="""
                    f""""{machine_name}") already exists."""
                )
                raise VersionAlreadyExists(msg)
            v.pages.all().delete()
            v.images.all().delete()
            v.sphinx_version = self.config["sphinx_version"]
            v.head = None
        else:
            v = Version(
                project=project,
                version=self.config["release"],
                sphinx_version=self.config["sphinx_version"],
            )
            v.save()
        return v

    def import_documents(self, package: tarfile.TarFile, version: Version) -> None:
        """
        Import all downloadable documents in our Sphinx documentation into the
        database (and our Django storage) before importing any pages.

        Args:
            package: the opened Sphinx documentation tarfile
            version: the :py:class:`Version` which which to associate our documents

        """
        for member in package.getmembers():
            if not member.isfile():
                continue
            path = Path(*Path(member.name).parts[1:])
            if path.suffix == "":
                continue
            if path.match("_downloads/*/*") and not path.name.startswith("."):
                fd = package.extractfile(member)
                orig_path: str = str(path)
                doc = SphinxDocument(version=version, orig_path=orig_path)
                doc.file.save(path.name, fd)
                doc.save()
                self.document_map[orig_path] = doc
                logger.info(
                    "%s.document.imported project=%s version=%s orig_path=%s "
                    "url=%s id=%s",
                    self.__class__.__name__,
                    version.project.machine_name,  # type: ignore[attr-defined]
                    version.version,
                    doc.orig_path,
                    doc.file.url,
                    doc.id,
                )

    def import_images(self, package: tarfile.TarFile, version: Version) -> None:
        """
        Import all images in our Sphinx documentation into the database before
        importing any pages, then return a lookup dict for doing ``<img
        src="image_path">`` replacements in the page bodies.

        Args:
            package: the opened Sphinx documentation tarfile
            version: the :py:class:`Version` which which to associate our images

        """
        for member in package.getmembers():
            if not member.isfile():
                continue
            path = Path(*Path(member.name).parts[1:])
            if path.match("_images/*") and not path.name.startswith("."):
                fd = package.extractfile(member)
                orig_path: str = str(path)
                image = SphinxImage(version=version, orig_path=orig_path)
                image.file.save(orig_path, fd)
                image.save()
                self.image_map[orig_path] = image
                logger.info(
                    "%s.image.imported project=%s version=%s orig_path=%s url=%s id=%s",
                    self.__class__.__name__,
                    version.project.machine_name,  # type: ignore[attr-defined]
                    version.version,
                    image.orig_path,
                    image.file.url,
                    image.id,
                )

    def _fix_page_title(self, path: str, data: Dict[str, Any]) -> None:
        """
        Ensure that there is a ``title`` key in ``data``, the JSON data from our
        .fjson file.  Some special pages don't have a ``title`` key in their
        JSON data, so we supply one based on their filename, or by copying
        another key from ``data``.

        Args:
            path: the file path in the tarfile data: the JSON data from our file
            data: the JSON data from our ``.fjson`` file

        """
        if "title" not in data:
            data["title"] = "UNKNOWN"
        if path in SphinxPage.SPECIAL_PAGES:
            data["title"] = SphinxPage.SPECIAL_PAGES[path]
        if data["title"] in self.ODD_TITLES:
            data["title"] = path
        if "title" not in data:
            # Some of the special pages don't have 'title' keys
            if "indextitle" in data:
                data["title"] = data["indextitle"]
            else:
                data["title"] = SphinxPage.SPECIAL_PAGES[path]

    def _fix_link_hrefs(self, path: str, body: str) -> str:
        """
        Given an HTML body of a Sphinx page, update the ``<a href="path">``
        references for "path" to be rendered at page render time.  If we don't
        do this, a lot of links won't work, because they do
        index page, instead of being relative to the root of the docs, and won't
        work.

        Args:
            path: the path to the current page
            body: the HTML body of a Sphinx document

        Returns:
            ``body`` with its ``<a>`` urls and updated

        """
        if not body:
            return ""

        # Parse the HTML body into an lxml tree
        html = lxml.html.fromstring(body)

        # Find all internal references except for download directives
        links = html.cssselect("a.reference.internal:not(.download)")

        # For each link, update its URL to be rendered at page render time
        for link in links:
            href = link.attrib["href"]
            anchor = None
            if "#" in href:
                href, anchor = href.split("#")
            if href.endswith("/"):
                href = href[:-1]
            # To deal with relative links, we need to know our current path
            # and then compute the absolute path from that.
            levels = href.count("../")
            if levels:
                href = re.sub("^(../)*", "", href)
                href = "/".join(path.split("/")[:-(levels)] + [href])
            link.attrib["href"] = (
                "{{% url 'sphinx_hosting:sphinxpage--detail' project_slug='{}' version='{}' path='{}' %}}".format(  # noqa:E501  # pylint: disable=line-too-long
                    self.config["project"], self.config["release"], href
                )
            )
            if anchor:
                link.attrib["href"] += f"#{anchor}"

        # Return the updated HTML body
        return lxml.html.tostring(html).decode("utf-8")

    def _fix_page_body(self, path: str, data: Dict[str, Any]) -> None:
        """
        Do any work needed to prepare the page body before inserting into the
        database.  This means:

        * Ensure the ``body`` key exists in ``data``
        * Update the ``img`` sources to point to our Django storage location.
          We uploaded them to our storage during :py:meth:`import_images`.
        * Update the ``href``s for any ``<a>`` links to be rendered at page
          render time.
        * Update the ``<table>``s to have the CSS classes we need for them to
          display nicely.

        Args:
            path: the path to the current page
            data: the JSON data from our file

        """
        if "body" not in data or data["body"] is None:
            # Ensure we always have data['body'] defined as a string, for when
            # we create the SphinxPage, below
            data["body"] = ""
        data["orig_body"] = data["body"]
        if data["body"]:
            # Update the img src for any images in data['body'] for to point to our
            # Django storage locations
            data["body"] = self._update_image_src(data["body"])
            # Update the img src for any images in data['body'] for to point to our
            # Django storage locations
            data["body"] = self._update_document_href(data["body"])
            # Update the hrefs for any <a> links to be absolute.  The relative
            # paths we get from Sphinx end up being relative to the Sphinx index
            # document instead of to the root of the docs
            data["body"] = self._fix_link_hrefs(path, data["body"])
            html = lxml.html.fromstring(data["body"])
            # remove the first <h1> -- we'll display the page title another way
            first_h1 = html.cssselect("h1")
            if first_h1:
                first_h1[0].getparent().remove(first_h1[0])
            # Fix our tables to look better
            tables = html.cssselect("table")
            for table in tables:
                wrapper = XML('<div class="table-responsive"></div>')
                parent = table.getparent()
                parent.append(wrapper)
                wrapper.insert(0, table)
                table.classes.add("table")
                table.classes.add("table-striped")
                table.classes.add("border")
                for tr in table.cssselect("thead > tr"):
                    tr.classes.discard("row-even")
                    tr.classes.discard("row-odd")
                for tr in table.cssselect("th"):
                    tr.classes.discard("head")
                    tr.classes.add("p-2")
                for tr in table.cssselect("tbody > tr"):
                    tr.classes.discard("row-even")
                    tr.classes.discard("row-odd")
                for div in table.cssselect("tbody > tr div.line"):
                    div.classes.discard("line")
                    div.classes.add("text-start")
                for div in table.cssselect("tbody > tr p"):
                    div.classes.add("text-start")
            data["body"] = lxml.html.tostring(html).decode("utf-8")
            # Unescape our template tags after lxml has converted our {% %}
            # to entities.
            tags = [m.group() for m in re.finditer(r"{%%20.*?%20%}", data["body"])]
            tags.extend(
                [m.group() for m in re.finditer(r"%7B%%20.*?%20%%7D", data["body"])]
            )
            for tag in tags:
                data["body"] = data["body"].replace(tag, urllib.parse.unquote(tag))
            # Convert the weird paragraph symbols to actual paragraph symbols
            data["body"] = re.sub(r"#61633;", r"para;", data["body"])

    def _fix_toc(self, data: Dict[str, Any]) -> None:
        """
        Update our page's local table of contents (``data['toc']`) to have the CSS
        classes we need in order for it to display properly.

        Args:
            data: the decoded JSON data of the sphinx page

        """
        if "toc" not in data:
            return
        data["orig_toc"] = data["toc"]
        html = lxml.html.fromstring(data["toc"])
        ul_first = html.cssselect("ul:first-child")[0]
        # Turn the first <ul> into a tabler vertical nav
        ul_first.classes.add("nav-vertical")
        # Turn all <uls> into nav-pills and nav
        for ul in html.cssselect("ul"):
            ul.classes.add("nav")
            ul.classes.add("nav-pills")
        # Make all list items into nav-items
        for li in html.cssselect("li"):
            li.classes.add("nav-item")
        # Make <a> into nav-links
        for link in html.cssselect("a"):
            link.classes.add("nav-link")
        # Now make the embedded uls collapsable
        for ul in html.cssselect("li > ul"):
            wrapper = XML(
                '<div class="d-flex flex-row justify-content-between align-items-center"></div>'  # noqa: E501
            )
            link = ul.getprevious()
            link.addprevious(wrapper)
            wrapper.insert(0, link)
            target = f"menu-{slugify(link.text_content())}"
            wrapper.append(
                XML(
                    '<a class="toc__toggle nav-link-toggle" data-bs-toggle="collapse" '
                    f'aria-expanded="false" data-bs-target="#{target}"></a>'
                )
            )
            ul.attrib["id"] = target
            ul.classes.add("collapse")
        try:
            link = html.cssselect("a:nth-child(2)")[0]
            link.attrib["aria-expanded"] = "true"
        except IndexError:
            pass
        try:
            ul = html.cssselect("li:first-child ul")[0]
            ul.classes.add("show")
        except IndexError:
            pass
        data["toc"] = lxml.html.tostring(html).decode("utf-8")

    def _update_page_tree(self, page: SphinxPage, data: Dict[str, Any]) -> None:
        """
        Update :py:attr:`page_tree`, our page linkage tree, with ``page``,
        which we will use in :py:meth:`link_pages` to set
        :py:attr:`SphinxPage.parent` and :py:attr:`SphinxPage.next_page`
        appropriately.

        Args:
            page: the :py:class:`sphinx_hosting.models.SphinxPage` object we created
            data: the JSON data from our page file

        """
        parent: Optional[str] = None  # noqa: FA100
        if data.get("parents"):
            parent = [p["title"] for p in data["parents"]][-1]
        next_title: Optional[str] = None  # noqa: FA100
        if data.get("next"):
            next_title = data["next"]["title"]
        self.page_tree[page.title] = PageTreeNode(
            page=page, parent_title=parent, next_title=next_title
        )

    def import_pages(self, package: tarfile.TarFile, version: Version) -> None:
        """
        Import a all pages from ``package`` into the database as
        :py:class:`sphinx_hosting.models.SphinxPage` objects, associating them
        with :py:class:`Version` ``version``.

        Args:
            package: the tarfile of the sphinx docs
            version: the :py:class:`Version` object to associated data

        Returns:
            The page linkage tree for consumption by :py:meth:`link_pages`.

        """
        for member in package.getmembers():
            path: str = str(Path(*Path(member.name).parts[1:]))
            if path.split("/")[-1].startswith("._"):
                # This is a Mac OS X AppleDouble hidden file.  Ignore it and
                # move on.  It just has MacOS specific metadata we don't care
                # about.
                continue
            if path.endswith(".fjson"):
                # files that contain page data will have a .fjson extension
                path = path.replace(".fjson", "")
                fd = cast(io.BufferedReader, package.extractfile(member))
                data = json.loads(fd.read())
                self._fix_page_title(path, data)
                self._fix_page_body(path, data)
                self._fix_toc(data)
                page = SphinxPage(
                    version=version,
                    relative_path=path,
                    content=json.dumps(data),
                    title=data["title"],
                    orig_body=data["orig_body"],
                    body=data["body"],
                    orig_local_toc=data.get("orig_toc", None),
                    local_toc=data.get("toc", None),
                    orig_global_toc=data.get("globaltoc", None),
                )
                page.save()
                self._update_page_tree(page, data)
                logger.info(
                    "%s.page.imported project=%s version=%s relpath=%s title=%s id=%s",
                    self.__class__.__name__,
                    version.project.machine_name,  # type: ignore[attr-defined]
                    version.version,
                    page.relative_path,
                    page.title,
                    page.id,
                )

    def link_pages(self) -> None:
        """
        Given :py:attr:`page_tree``, a list of page linkages (parent, next,
        prev), link all the :py:class:`sphinx_hosting.models.SphinxPage` objects
        in that list to their next page and their parent page.

        Args:
            tree: the page linkage tree

        """
        for link in self.page_tree.values():
            page = link.page
            logger.info(
                "%s.page.linking relpath=%s title=%s id=%s",
                self.__class__.__name__,
                page.relative_path,
                page.title,
                page.id,
            )
            if link.parent_title:
                page.parent = self.page_tree[link.parent_title].page
                logger.info(
                    "%s.page.linked-parent relpath=%s title=%s parent=%s",
                    self.__class__.__name__,
                    page.relative_path,
                    page.title,
                    page.parent.title,
                )
            if link.next_title:
                page.next_page = self.page_tree[link.next_title].page
                logger.info(
                    "%s.page.linked-next relpath=%s title=%s next=%s",
                    self.__class__.__name__,
                    page.relative_path,
                    page.title,
                    page.next_page.title,
                )
            page.save()

    def run(
        self,
        filename: Optional[str] = None,  # noqa: FA100
        file_obj: Optional[IO] = None,  # noqa: FA100
        force: bool = False,
    ) -> Version:
        """
        Load the pages in the tarfile identified by ``filename`` into
        the database as :py:class:`Version` ``version`` of :py:class:`Project`
        ``project``.  See the class docs for :py:class:`SphinxPackageImporter` for
        more background on how to prepare the package named by ``filename``.

        Keyword Args:
            filename: the filename of the gzipped tar archive of the Sphinx pages
            file_obj: an open file object of the gzipped tar archive of the Sphinx pages
            force: if ``True``, overwrite the docs for an existing version

        Raises:
            Project.DoesNotExist: no :py:class:`Project` exists whose
                ``machine_name`` matches the slugified ``project`` setting
                in the Sphinx package's ``conf.py``
            VersionAlreadyExists: a :py:class:`Version` with version string
                ``release`` from the Sphinx package's ``conf.py``
                already exists for our project, and ``force`` was not ``True``

        """
        assert not all(  # noqa: S101
            [filename, file_obj]
        ), 'provide either "filename" or "file_obj" but not both'
        with tarfile.open(name=filename, fileobj=file_obj) as package:
            self.load_config(package)
            version = self.get_version(force=force)
            self.import_images(package, version)
            self.import_documents(package, version)
            self.import_pages(package, version)
            self.link_pages()
        # Point version.head at the top page of the documentation set
        version.head = SphinxPage.objects.get(
            version=version, relative_path=self.config["root_doc"]
        )
        version.save()
        # Mark the appropriate pages as indexable
        version.mark_searchable_pages()
        project = version.project
        changed: bool = False
        if project.latest_version is None:  # type: ignore[attr-defined]
            project.latest_version = version  # type: ignore[attr-defined]
            project.save()  # type: ignore[attr-defined]
            changed = True
        elif not any(
            fnmatch.fnmatch(version.version, glob) for glob in EXCLUDE_FROM_LATEST
        ):
            if semver.compare(project.latest_version.version, version.version) < 0:  # type: ignore[attr-defined]
                # The new version is greater than the current latest version,
                # so update the latest version to be this new version
                SphinxPageIndex().remove_version(project.latest_version)  # type: ignore[attr-defined]
                project.latest_version = version  # type: ignore[attr-defined]
                project.save()  # type: ignore[attr-defined]
                changed = True
        if changed:
            # Reindex the project.  We do this here because we want to reindex the
            # update the "is_latest" flag on all pages in all versions of the
            # project in case this is now the latest version.
            #
            # In the logs you may see two reindexing events for the same
            # project.  The first
            SphinxPageIndex().reindex_project(cast(Project, version.project))
        return version
