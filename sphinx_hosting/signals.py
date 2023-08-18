from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from haystack import signals

from .models import SphinxPage, Version
from .search_indexes import SphinxPageIndex


class SphinxHostingSignalProcessor(signals.BaseSignalProcessor):

    def setup(self):
        # Listen only to the ``User`` model.
        models.signals.post_save.connect(self.handle_save, sender=SphinxPage)
        models.signals.post_delete.connect(self.handle_delete, sender=SphinxPage)

    def teardown(self):
        # Disconnect only for the ``User`` model.
        models.signals.post_save.disconnect(self.handle_save, sender=SphinxPage)
        models.signals.post_delete.disconnect(self.handle_delete, sender=SphinxPage)


@receiver(post_delete, sender=Version)
def reindex_project(sender, instance: Version, **kwargs):
    """
    Reindex all pages for all versions for the project related to ``instance``.
    We need to do this whenever a :py:class:`sphinx_hosting.models.Version` is
    deleted beacuse the project's latest version may have changed, and thus
    we need to change the ``is_latest`` field on all pages for that project.

    Args:
        instance: The version whose project we want to reindex.
    """
    SphinxPageIndex().reindex_project(instance.project)
