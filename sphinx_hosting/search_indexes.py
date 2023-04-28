from typing import List, Type

from django.db.models import Model, QuerySet
from haystack import indexes

from .models import SphinxPage


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
