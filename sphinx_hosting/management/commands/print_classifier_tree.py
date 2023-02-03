from django.core.management.base import BaseCommand
from rich.tree import Tree
from rich import print as rich_print

from sphinx_hosting.models import Classifier, ClassifierNode


class TreePrinter:
    """
    Parse the tree of :py:class:`sphinx_hosting.models.ClassifierNode` objects
    we get from :py:meth:`sphinx_hosting.models.ClassifierManager.tree` and
    print them to stdout in a pretty format.
    """

    def __init__(self) -> None:
        self.classifier_tree = Classifier.objects.tree()
        self.tree: Tree = Tree('Classifiers')
        for node in self.classifier_tree.values():
            branch = self.tree.add(self.title(node))
            self.build(branch, node)

    def title(self, node: ClassifierNode) -> str:
        if node.classifier:
            return f'{node.title} (ID: {node.classifier.id})'
        return node.title

    def build(self, branch: Tree, node: ClassifierNode) -> None:
        if node.items:
            for child in node.items.values():
                leaf = branch.add(self.title(child))
                self.build(leaf, child)

    def print(self) -> None:
        rich_print(self.tree)


class Command(BaseCommand):
    """
    **Usage**: ``./manage.py print_classifier_tree``

    Print the :py:class:`Classifier` hierarchy.
    """
    help = ('Print the Classifier hierarchy.')

    def handle(self, *args, **options) -> None:
        TreePrinter().print()
