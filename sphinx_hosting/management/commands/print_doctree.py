from argparse import ArgumentParser
from typing import cast

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from rich.tree import Tree
from rich import print as rich_print

from sphinx_hosting.models import SphinxPage, Version, TreeNode


class TreePrinter:
    """
    Parse the tree of :py:class:`sphinx_hosting.models.TreeNode` objects
    we get from :py:meth:`sphinx_hosting.models.Version.page_tree` and
    print them to stdout in a pretty format.
    """

    def __init__(self, version: Version):
        self.sphinx_tree = version.page_tree
        self.tree: Tree = Tree(self.title(self.sphinx_tree.head))
        self.build(self.tree, cast(TreeNode, self.sphinx_tree.head))

    def title(self, node: TreeNode) -> str:
        return f'{node.title} [{cast(SphinxPage, node.page).id}]'

    def build(self, branch: Tree, node: TreeNode):
        if node.children:
            for child in node.children:
                leaf = branch.add(self.title(child))
                self.build(leaf, child)

    def print(self):
        rich_print(self.tree)


class Command(BaseCommand):
    """
    **Usage**: ``./manage.py print_doctree <project_machine_name> <version number>``

    Print the page tree for a :py:class:`Version`
    """
    args = '<tarfile>'
    help = 'Print the deduced page hierarchy for a version of a project.'

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

    def handle(self, *args, **options) -> None:
        try:
            version = Version.objects.get(
                project__machine_name=slugify(options['project']),
                version=options['version']
            )
        except Version.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(str(e)))

        self.stdout.write(self.style.SUCCESS(f'\n{version.project.title}: {version.version}\n'))
        TreePrinter(version).print()
