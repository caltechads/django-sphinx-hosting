Management commands
===================

import_docs
-----------

:synposis: Imports a tarfile of Sphinx documentation pages in JSON form into the database.

The ``import_docs`` command imports a tarfile of Sphinx pages in JSON format
into our database.   This command is a thin shim around
:py:class:`sphinx_hosting.importers.SphinxPackageImporter`, so look there for details
of what it is doing.

Usage
^^^^^

.. important::

  Before importing, there must be a :py:class:`sphinx_hosting.models.Project` in
  the database whose ``machine_name`` matches the ``project`` in Sphinx's
  ``conf.py`` config file for the docs to be imported.

In the Sphinx docs subfolder of the package of which you want to produce a tarfile,
you will want to build your docs as ``json``, not ``html`` as is usual.

Do either::

    make json

or::

    sphinx-build -n -b json build/json

To build the tarfile, the files in the tarfile should be contained in a folder.  We want::

    folder/py-modindex.fjson
    folder/globalcontext.json
    folder/_static
    folder/last_build
    folder/genindex.fjson
    folder/objectstore.fjson
    folder/index.fjson
    folder/environment.pickle
    folder/searchindex.json
    folder/objects.inv
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


Here's how you do that::

    cd build
    tar zcf mydocs.tar.gz json

To load that tarfile into the database::

  $ ./manage.py import_docs mydocs.tar.gz

To load the export and overwite any existing Sphinx pages in the database with that in the tarfile::

  $ ./manage.py import_docs --force mydocs.tar.gz