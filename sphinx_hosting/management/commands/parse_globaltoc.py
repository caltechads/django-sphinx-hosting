from argparse import ArgumentParser
from pprint import pprint

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from sphinx_hosting.models import Version
from sphinx_hosting.models import SphinxGlobalTOCHTMLProcessor


class Command(BaseCommand):
    """
    **Usage**: ``./manage.py print_globaltoc <project_machine_name> <version number>``

    Print the global table of contents for a :py:class:`Version`.
    """
    args = '<project_machine_name> <version_number>'
    help = ('Print the deduced page hierarchy for a version of a project.')

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            'project',
            metavar='project_machine_name',
            type=str,
            help='The machine_name of the project.'
        )
        parser.add_argument(
            'version',
            metavar='version_number',
            type=str,
            help='The version number for which we want to print a page tree.'
        )
        parser.add_argument(
            'verbose',
            action='store_true',
            default=False,
            help='Increase verbosity.'
        )

    def handle(self, *args, **options) -> None:
        try:
            version = Version.objects.get(
                project__machine_name=slugify(options['project']),
                version=options['version']
            )
        except Version.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(str(e)))
            return

        pprint(SphinxGlobalTOCHTMLProcessor().run(version, verbose=options['verbose']))
