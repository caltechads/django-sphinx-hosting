from typing import List, Type, Optional

from django.db.models import Model, QuerySet
from haystack import indexes

from .models import SphinxPage, Project, Version


class SphinxPageIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True)
    project_id = indexes.CharField(model_attr='version__project__id', faceted=True)
    project = indexes.CharField(model_attr='version__project__machine_name')
    version_id = indexes.CharField(model_attr='version__id')
    classifiers = indexes.MultiValueField(faceted=True)
    modified = indexes.DateTimeField(model_attr='modified')
    is_latest = indexes.CharField(faceted=True)

    def get_model(self) -> Type[Model]:
        return SphinxPage

    def prepare_is_latest(self, obj: SphinxPage) -> str:
        """
        Elasticsearch doesn't know how to deal with Python boolean values, so we set
        a string key on our document to either ``true`` or ``false`` depending on
        whether this page is part of the most recent version for a project or not.

        Args:
            obj: The page we're indexing

        Returns:
            Either ``true`` or ``false``.
        """
        is_latest = obj.version == obj.version.project.latest_version
        if is_latest:
            return 'true'
        return 'false'

    def prepare_classifiers(self, obj: SphinxPage) -> List[str]:
        return [classifier.name for classifier in obj.version.project.classifiers.all()]

    def index_queryset(self, using=None) -> QuerySet:
        """
        Used when the entire index for model is updated.
        """
        return self.get_model().objects.filter(searchable=True)

    def reindex_project(
        self,
        project: Project,
        exclude: Optional[Version] = None,
    ) -> None:
        """
        Reindex all pages for a project.  We need to do this whenever a
        :py:class:`sphinx_hosting.models.Version` is published,
        unpublished, or deleted.

        .. note::
            If we have a lot of pages in a lot of versions for this project,
            this could take a while.  We should probably look into a way to
            do this asynchronously.

        Args:
            project: The project whose pages we want to reindex.

        Keyword Args:
            exclude: A version to exclude from the reindexing.  This is used
                when a version has just been imported because it will have
                already been indexed by the import process.
        """
        qs = self.index_queryset().filter(version__project=project)
        if exclude:
            qs = qs.exclude(version=exclude)
        backend = self.get_backend(None)
        if backend is not None:
            batch_size: int = backend.batch_size
            total: int = qs.count()
            # We need to update the index in batches because we can run into
            # backend transport errors if we try to update too many documents at
            # once.
            for start in range(0, total, batch_size):
                end = min(start + batch_size, total)
                backend.update(self, qs[start:end])
