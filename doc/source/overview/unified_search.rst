Unified Search
==============

``django-sphinx-hosting`` exposes one global search page that can blend
built-in ``SphinxPage`` hits with host-project models in the same ranked result
list. Users search once and receive one paginated list ordered by the
Haystack/OpenSearch backend's relevance score, without model-specific grouping.


How unified search works
------------------------

The global search view always includes built-in ``SphinxPage`` results. Host
projects may opt additional models into the same result list by providing:

* a Haystack ``SearchIndex`` for the model
* a ``SEARCH_RESULT_RENDERERS`` entry that tells ``django-sphinx-hosting`` how
  to render one hit for that model

At request time, ``django-sphinx-hosting``:

* starts from the Haystack query created by the standard search form
* restricts the query to ``SphinxPage`` plus the registered host models
* preserves the backend-provided ordering
* dispatches each ``SearchResult`` to the built-in ``SphinxPage`` card or the
  registered host-model renderer

The application does not add model-based boosts, tie-breakers, or grouping.
Mixed-model ranking quality therefore depends on comparable search-index design
across the participating models.


Built-in results
----------------

Built-in ``SphinxPage`` hits continue to use the package's existing search
result card. No extra configuration is required for them.


Extending unified search with your own model
--------------------------------------------

To add a host-project model to unified search, do all of the following:

1. Define a searchable Django model.
2. Create a Haystack ``SearchIndex`` for that model.
3. Register a search-result renderer in ``SPHINX_HOSTING_SETTINGS``.

Example model
^^^^^^^^^^^^^

.. code-block:: python

   from django.db import models

   class SearchNote(models.Model):
      title = models.CharField(max_length=200)
      body = models.TextField()
      project = models.ForeignKey("sphinxhostingcore.Project", on_delete=models.CASCADE)
      classifiers = models.ManyToManyField("sphinxhostingcore.Classifier", blank=True)

Example ``SearchIndex``
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from haystack import indexes

   from .models import SearchNote

   class SearchNoteIndex(indexes.SearchIndex, indexes.Indexable):
      text = indexes.CharField(document=True)
      project_id = indexes.CharField(model_attr="project__id", faceted=True)
      classifiers = indexes.MultiValueField(faceted=True)
      title = indexes.CharField(model_attr="title")
      body = indexes.CharField(model_attr="body")

      def get_model(self):
         return SearchNote

      def prepare_text(self, obj):
         return f"{obj.title}\\n\\n{obj.body}"

      def prepare_classifiers(self, obj):
         return [classifier.name for classifier in obj.classifiers.all()]

Example renderer
^^^^^^^^^^^^^^^^

.. code-block:: python

   from wildewidgets import Block, LinkButton

   def render_search_note_result(*, result, request, user, view):
      del request, user, view
      note = result.object
      return Block(
         Block(note.title, tag="h3"),
         Block(note.body[:200]),
         LinkButton(text="View Project", url=note.get_absolute_url()),
      )

Example settings
^^^^^^^^^^^^^^^^

.. code-block:: python

   SPHINX_HOSTING_SETTINGS = {
      "SEARCH_RESULT_RENDERERS": {
         "core.SearchNote": "demo.core.search.render_search_note_result",
      },
   }


Facet participation
-------------------

If a host model should participate in the global ``project`` and ``classifier``
facets, its ``SearchIndex`` must expose the same faceted field names used by
the built-in ``SphinxPage`` search index:

* ``project_id``
* ``classifiers``

When using the installed ``django-haystack-opensearch`` backend, global search
applies exact facet filters through Haystack narrow queries. The backend maps
those exact filters to the correct OpenSearch facet field names, including
``.keyword`` subfields for text-based faceted fields.

Models without those fields may still be searchable, but they will not respond
to project/classifier facet filtering.


Validation and failure modes
----------------------------

``SEARCH_RESULT_RENDERERS`` is validated at request time.

* The setting must be a dict.
* Each key must be a Django model label string.
* Each value must be a dotted-path string.
* Each configured model must resolve to an installed Django model.
* Each configured model must also have a registered Haystack ``SearchIndex``.
* Each imported renderer target must be callable.

Renderer exceptions are not swallowed. If a renderer fails, the request will
fail so the host project can fix the configuration or implementation bug.


Demo application
----------------

The demo app in ``sandbox/demo`` includes a complete working example:

* ``demo.core.models.SearchNote``
* ``demo.core.search_indexes.SearchNoteIndex``
* ``demo.core.search.render_search_note_result``
* ``SPHINX_HOSTING_SETTINGS["SEARCH_RESULT_RENDERERS"]``

That demo setup is the reference implementation for host-project extensions.
