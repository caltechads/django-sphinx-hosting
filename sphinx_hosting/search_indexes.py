import time
from typing import List, Type

from django.db.models import Model, QuerySet, F
import elasticsearch.exceptions
from haystack import indexes

from .logging import logger
from .models import SphinxPage, Project, Version


class SphinxPageIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True)
    project_id = indexes.CharField(model_attr='version__project__id', faceted=True)
    project = indexes.CharField(model_attr='version__project__machine_name')
    version_id = indexes.CharField(model_attr='version__id')
    classifiers = indexes.MultiValueField(faceted=True)
    modified = indexes.DateTimeField(model_attr='modified')

    def get_model(self) -> Type[Model]:
        return SphinxPage

    def prepare_classifiers(self, obj: SphinxPage) -> List[str]:
        return [classifier.name for classifier in obj.version.project.classifiers.all()]

    def index_queryset(self, using=None) -> QuerySet:
        """
        Used when the entire index for model is updated.
        """
        return self.get_model().objects.filter(searchable=True).filter(version__project__latest_version=F('version'))

    def remove_version(self, version: Version) -> None:
        """
        Remove all pages for a version from the index.

        Args:
            version_id: The version whose pages we want to remove from the index.
        """
        qs = self.get_model().objects.filter(version__id=version.pk).filter(searchable=True)
        logger.info('Removing %d pages from the search index for version %s', qs.count(), version)
        for obj in qs:
            self.remove_object(obj)

    def reindex_project(self, project: Project) -> None:  # type: ignore[note]
        """
        Reindex all pages for a project.  This happens when we get a new
        latest_version for the project.

        .. note::
            If we have a lot of pages in our latest version for this project,
            this could take a while.  We should probably look into a way to
            do this asynchronously.

        Args:
            project: The project whose pages we want to reindex.
        """
        # This should only ever return a QuerySet of SphinxPage objects
        # that match the latest version of a project.

        # self.index_queryset() is a queryset of SphinxPage objects, so
        # our filters are on SphinxPage fields.
        qs = (
            self.index_queryset()
            .filter(version__project=project)
        )
        backend = self.get_backend(None)
        if backend is not None:
            batch_size: int = backend.batch_size
            total: int = qs.count()
            # We need to update the index in batches because we can run into
            # backend transport errors if we try to update too many documents at
            # once.
            for start in range(0, total, batch_size):
                end = min(start + batch_size, total)
                while True:
                    try:
                        backend.update(self, qs[start:end])
                    except elasticsearch.exceptions.TransportError as e:
                        # We're using the Elasticsearch backend, check the status_code
                        # from the exception to see if we can recover from it.
                        #
                        if e.status_code == 429:
                            # We're being rate limited, so sleep for a bit and try again.
                            # The problem here is we could sleep so long we exceed our gunicorn,
                            # nginx, or other timeout.  We should probably look into a way to
                            # do this asynchronously.
                            logger.warning(
                                'Elasticsearch rate limit reached.  Sleeping for 5 seconds.'
                            )
                            time.sleep(5)
                    else:
                        break
