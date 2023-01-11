*************************************
Packaging your Sphinx docs for import
*************************************

``django-sphinx-hosting`` expects your Sphinx docs to be in a specific format
to be able to be imported.  On this page, we describe how to package your
documents in this way.

``django-sphinx-hosting`` expects to be handed a gzipped tarfile of the ouput
of Sphinx's ``make json``, and expects the ``project`` and ``release``.

Sphinx conf.py settings
=======================

project
-------

To import a documentation set, there must be a
:py:class:`sphinx_hosting.models.Project` in the database whose slugified
``machine_name`` matches the ``project`` in Sphinx's ``conf.py`` config file for
the docs to be imported.

For example, if you set the ``project`` key to ``foobar-baz`` in ``conf.py`` the
associated project should be created like so if you were doing it from the command
line::

    >>> from sphinx_hosting.models import Project
    >>> project = Project(
        title="Foobar Baz",
        machine_name="foobar-baz",
        description="my description"
    )
    >>> project.save()

Normally, of course, you would use the ``django-sphinx-hosting`` web interface to
create your project record.

release
-------

The ``release`` in the ``conf.py`` will be used to create or update a
:py:class:`sphinx_hosting.models.Version`.  We will set
:py:attr:`sphinx_hosting.models.Version.version` to the value of ``release``.


Packaging your documentation set
================================

In your Sphinx docs folder, you will want to build your docs as ``json``, not
``html``.

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