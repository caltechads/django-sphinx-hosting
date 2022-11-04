import logging
import json
from pathlib import Path
import tarfile
from typing import Dict

import lxml.html

from .exc import VersionAlreadyExists
from .models import Project, Version, SphinxPage, SphinxImage

ImageMap = Dict[str, SphinxImage]

logger = logging.getLogger('sphinx_hosting.importers')


class SphinxPackageImporter:
    """
    Import a tarfile of a built set of Sphinx documentation into the database.

    The documentation package should have been built via the ``json`` output from
    ``sphinx-build``, so either::

        make json

    or::

        sphinx-build -n -b json build/json

    Then the tarfile should be built like so::

        cd build
        tar zcf mydocs.tar.gz json
    """

    def __init__(self) -> None:
        self.image_map: ImageMap = {}   #: Used to map original Sphinx image paths to our Django storage path

    def _update_image_src(self, body: str) -> str:
        """
        Given an HTML body of a Sphinx page, update the ``<img src="path">``
        references to point to the URLs for our uploaded :py:class:`SphinxImage`
        objects.

        Args:
            body: the HTML body of a Sphinx document

        Returns:
            ``body`` with its `<img>` urls updated
        """
        if not body:
            return ''
        html = lxml.html.fromstring(body)
        images = html.cssselect('img')
        for image in images:
            if image.attrib['src'] in self.image_map:
                image.attrib['src'] = self.image_map[image.attrib['src']].file.url
        return lxml.html.tostring(html).decode('utf-8')

    def get_version(self, package: tarfile.TarFile, force: bool = False) -> Version:
        """
        Look in ``package`` for a member named ``globalcontext.json``, and load
        that file as JSON.

        Extract these things from that JSON:

            * the version string from the ``release`` key.
            * the ``machine_name`` of the :py:class:`Project` for this
              documentation tarfile

        Return a new :py:class:`Version` instance on the project

        Args:
            package: the opened Sphinx documentation tarfile

        Keyword Args:
            force: if ``True``, re-use an existing version, purging any docs and
                images associated with it first

        Raises:
            Project.DoesNotExist: no :py:class:`Project` with machine_name
                ``machine_name`` exists
            VersionAlreadyExists: a :py:class:`Version` with version string
                ``version`` already exists for our project
        """
        names = [member for member in package.getnames() if member.endswith('/globalcontext.json')]
        if not names:
            raise KeyError('Sphinx docs TarFile has no globalcontext.json')
        data = json.loads(package.extractfile(names[0]).read())
        project = Project.objects.get(machine_name=data['project'])
        v = project.versions.filter(version=data['release']).first()
        if v:
            if not force:
                raise VersionAlreadyExists(
                    f"""Version {data['release']} of Project(machine_name="{data['project']}") already exists."""
                )
            v.pages.all().delete()
            v.images.all().delete()
        else:
            v = Version(project=project, version=data['release'])
            v.save()
        return v

    def import_images(self, package: tarfile.TarFile, version: Version) -> None:
        """
        Import all images in our Sphinx documentation into the database before
        importing any pages, then return a lookup dict for doing ``<img
        src="image_path">`` replacements in the page bodies.

        Args:
            package: the opened Sphinx documentation tarfile
            version: the :py:class:`Version` which which to associate our images

        Returns:
            A mapping of original filename to :py:class:`SphinxImage`
        """
        for member in package.getmembers():
            path = Path(member.name)
            if path.match('*/_images/*'):
                fd = package.extractfile(member)
                orig_path = Path(*path.parts[1:])
                image = SphinxImage(version=version, orig_path=orig_path, file=fd)
                image.save()
                self.image_map[member.name] = image
                logger.info(
                    "%s.image.imported project=%s version=%s orig_path=%s url=%s id=%s",
                    self.__class__.__name__,
                    version.project.machine_name,
                    version.version,
                    image.orig_path,
                    image.file.url,
                    image.id
                )

    def import_pages(self, package: tarfile.TarFile, version: Version) -> SphinxPage:
        """
        Import a single page into the database, associating it with
        :py:class:`Version` ``version``.

        Args:
            data: the decoded JSON data of the sphinx page
            version: the :py:class:`Version` object to associated data

        Returns:
            The completed :py:class:`SphinxPage`
        """
        for member in package.getmembers():
            path = Path(member.name)
            if path.suffix == '.fjson':
                data = json.loads(package.extractfile(member).read())
                if 'title' not in data:
                    if 'indextitle' in data:
                        data['title'] = data['indextitle']
                    else:
                        data['title'] = SphinxPage.SPECIAL_TITLES[Path(path.parts[-1]).stem]
                if 'body' not in data or data['body'] is None:
                    data['body'] = ''

                # Update the img src for to point to our Django storage locations
                data['body'] = self._update_image_src(data['body'])
                relpath = Path(*path.parts[1:])
                page = SphinxPage(
                    version=version,
                    relative_path=relpath.stem,
                    content=json.dumps(data),
                    title=data['title'],
                    body=data['body']
                )
                page.save()
                logger.info(
                    "%s.page.imported project=%s version=%s relpath=%s title=%s id=%s",
                    self.__class__.__name__,
                    version.project.machine_name,
                    version.version,
                    page.relative_path,
                    page.title,
                    page.id
                )

    def run(self, filename: str, force: bool = False) -> None:
        """
        Load the pages in the tarfile identified by ``filename`` into
        the database as :py:class:`Version` ``version`` of :py:class:`Project`
        ``project``.

        The :py:class:`Project` named by ``machine_name`` must exist in the
        database before you run this.

        Note:
            The Sphinx docs in the tarfile should be in ``.tjson`` format, which
            you get in the usual Sphinx folder by doing::

                make json

            The files in the tarfile be contained in a folder.  We want::

                mypackage/py-modindex.fjson
                mypackage/globalcontext.json
                mypackage/_static
                mypackage/last_build
                mypackage/genindex.fjson
                mypackage/objectstore.fjson
                mypackage/index.fjson
                mypackage/environment.pickle
                mypackage/searchindex.json
                mypackage/objects.inv
                ...

            Not::

                py-modindex.fjson
                globalcontext.json
                _static
                last_build
                genindex.fjson
                index.fjson
                environment.pickle
                searchindex.json
                objects.inv
                ...

        Args:
            filename: the filename of the gzipped tar archive of the Sphinx pages
            force: if ``True``, overwrite the docs for an existing version

        Raises:
            Project.DoesNotExist: no :py:class:`Project` with machine_name
                ``machine_name`` exists
            VersionAlreadyExists: a :py:class:`Version` with version string
                ``version`` already exists for our project
        """
        with tarfile.open(filename) as package:
            version = self.get_version(package, force=force)
            self.import_images(package, version)
            self.import_pages(package, version)
