from __future__ import annotations

from haystack import indexes

from .models import SearchNote


class SearchNoteIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Haystack index for demo ``SearchNote`` objects.
    """

    #: The primary full-text document for this search index.
    text = indexes.CharField(document=True)
    #: The related project identifier used for unified-search facets.
    project_id = indexes.CharField(model_attr="project__id", faceted=True)
    #: The related classifier names used for unified-search facets.
    classifiers = indexes.MultiValueField(faceted=True)
    #: The title stored for search-result rendering.
    title = indexes.CharField(model_attr="title")
    #: The body stored for search-result rendering.
    body = indexes.CharField(model_attr="body")
    #: The modified timestamp stored for search-result rendering.
    modified = indexes.DateTimeField(model_attr="modified")

    def get_model(self) -> type[SearchNote]:
        """
        Return the indexed Django model.

        Returns:
            The ``SearchNote`` model class.

        """
        return SearchNote

    def prepare_text(self, obj: SearchNote) -> str:
        """
        Build the unified-search document for one note.

        Args:
            obj: The note being indexed.

        Returns:
            The text document sent to Haystack/OpenSearch.

        """
        return f"{obj.title}\n\n{obj.body}"

    def prepare_classifiers(self, obj: SearchNote) -> list[str]:
        """
        Prepare classifier facet values for one note.

        Args:
            obj: The note being indexed.

        Returns:
            The classifier names attached to the note.

        """
        return [classifier.name for classifier in obj.classifiers.all()]

    def index_queryset(self, using: str | None = None):  # noqa: ARG002
        """
        Return the queryset used for bulk indexing.

        Keyword Args:
            using: The Haystack connection alias. Unused.

        Returns:
            The queryset of notes eligible for unified search.

        """
        return self.get_model().objects.select_related("project").prefetch_related(
            "classifiers"
        )
