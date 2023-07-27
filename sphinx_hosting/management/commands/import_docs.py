from argparse import ArgumentParser

from django.core.management.base import BaseCommand

from sphinx_hosting.exc import VersionAlreadyExists
from sphinx_hosting.models import Project
from sphinx_hosting.importers import SphinxPackageImporter


class Command(BaseCommand):
    """
    Import a Sphinx documentation tarfile into the database.

    We will use the the slugified version (converted to only letters, numbers,
    dashes and underscores) of the ``project`` variable from the Sphinx
    ``conf.py`` that built the tarfile as the ``machine_name`` of the
    :py:class:`Project` to load into, and we will use the "release" variable
    from ``conf.py`` to build the :py:class:`Version` object to load into.

    The Sphinx documentation tarfile should have been built via the``json``
    output from ``sphinx-build``, either::

        make json

    or::

        sphinx-build -n -b json build/json

    Then the tarfile should be built like so::

        cd build
        tar zcf mydocs.tar.gz json

    The files in the resulting tarfile should be contained in a folder.  We
    something like::

        json/py-modindex.fjson
        json/globalcontext.json
        json/_static
        json/last_build
        json/genindex.fjson
        json/objectstore.fjson
        json/index.fjson
        json/environment.pickle
        json/searchindex.json
        json/objects.inv
        ...

    """
    args = '<tarfile>'
    help = 'Imports a tarfile of Sphinx documentation into a pre-existing project.'

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            'tarfile',
            metavar='tarfile',
            type=str,
            help='The filename of the tarfile to import.'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            default=False,
            help='Overwrite documentation for any matching existing version.'
        )

    def handle(self, *args, **options) -> None:
        importer = SphinxPackageImporter()
        try:
            version = importer.run(filename=options['tarfile'], force=options['force'])
        except VersionAlreadyExists as e:
            self.stdout.write(self.style.ERROR(str(e)))
        except Project.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(str(e)))
        self.stdout.write(
            self.style.SUCCESS(
                f'Imported to Version(id={version.id}) of '
                f'Project(id={version.project.id}, title={version.project.title})'
            )
        )
