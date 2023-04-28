Importing your Sphinx docs
==========================

Before importing your docs, ensure that you have configured your Sphinx project
properly for ``django-sphinx-hosting`` by following the instructions on
:doc:`/overview/packaging`.

Packaging
---------

In order to be able to be imported into ``django-sphinx-hosting``,  you will need to
publish your Sphinx docs as JSON files, and to bundle them in a specific way.

In your Sphinx docs folder, you will want to build your docs as ``json``, not
``html``.

Do either::

    make json

or::

    sphinx-build -n -b json build/json

To build the tarfile, the files in the tarfile should be contained in a folder.  We want::

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

Not::

    py-modindex.fjson
    globalcontext.json
    _static
    last_build
    genindex.fjson
    index.fjson
    environment.pickle
    searchindex.json
    objects.inv
    ...


Here's how you do that:

.. code-block:: shell

    $ cd build
    $ tar zcf mydocs.tar.gz json

Now you can import ``mydocs.tar.gz`` into ``django-sphinx-hosting``.

Importing
---------

There are three ways to import your package into ``django-sphinx-hosting``:

* Use the upload form on the project's detail page.
* Use the API endpoint ``/api/v1/version/``.
* Use the ``import_docs`` Django management command.


The upload form
^^^^^^^^^^^^^^^

To use the upload form, browse to the project detail page of the project whose
docs you want to import, and use the form titled "Import Docs" in the "Actions"
column along the left side of the page.

.. note::

    You must have the ``sphinxhostingcore.change_project`` Django permission or
    be a Django superuser in order to use the upload form.  Either assign that
    directly to your Django user object, or use assign your user to either the
    "Administrators" or "Editors" Django groups to get that permission.  See
    :doc:`/overview/authorization`


Use the API endpoint
^^^^^^^^^^^^^^^^^^^^

To upload your docs package via the API, you must submit as form-data, with a
single key named ``file``, and with the ``Content-Disposition`` header like
so::

    Content-Disposition: attachment;filename=mydocs.tar.gz

The filename you pass in the ``Content-Disposition`` header does not matter and
is not used; set it to whatever you want.

To upload a file with ``curl`` to the endpoint for this view:

.. code-block:: shell

    curl \
        -XPOST \
        -H "Authorization: Token __THE_API_TOKEN__" \
        -F 'file=@path/to/yourdocs.tar.gz' \
        https://sphinx-hosting.example.com/api/v1/version/import/


The ``import_docs`` management command
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Load your tarfile into the database::

  $ ./manage.py import_docs mydocs.tar.gz

To load the export and overwite any existing Sphinx pages in the database with
that in the tarfile::

  $ ./manage.py import_docs --force mydocs.tar.gz