*******************************
Configuring your Sphinx project
*******************************

``django-sphinx-hosting`` expects your Sphinx docs to be in a specific format to
be able to be imported, and to be built with specific sphinx extensions.  On
this page, we describe how to configure your Sphinx project appropriately.

Sphinx conf.py settings
=======================

project
-------

To import a documentation set, there must be a
:py:class:`sphinx_hosting.models.Project` in the database whose slugified
``machine_name`` matches the ``project`` in Sphinx's ``conf.py`` config file for
the docs to be imported.

To determine the proper ``machine_name`` for your ``conf.py``, create a project
via the "Create Project" button on the project listing page, then view or edit
the project to see the ``machine_name`` that got generated for you.

release
-------

The ``release`` in the ``conf.py`` will be used to create or update a
:py:class:`sphinx_hosting.models.Version`.  We will set
:py:attr:`sphinx_hosting.models.Version.version` to the value of ``release``.


extensions
----------

sphinx_rtd_theme [required]
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Miminally, you must use the `Sphinx ReadTheDocs theme
<https://github.com/readthedocs/sphinx_rtd_theme>`_ when packaging your
documentation.  The importers, views and stylesheets inside
django-sphinx-hosting depend on the HTML structure, Javascript and CSS classes
that that theme provides.

Ensure that you have ``html_theme_options["collapse_navigation"]`` set to
``False``, otherwise your auto-built navigation within django-sphinx-hosting
may look wrong.

.. code-block:: python

    extensions = [
        'sphinx_rtd_theme',
        ...
    ]

    html_theme = 'sphinx_rtd_theme'
    html_theme_options = {
        "collapse_navigation": False
    }

sphinxcontrib-jsonglobaldoc [optional]
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have a complex page hierarchy in your documentation, you may benefit from
`sphinxcontrib-jsonglobaltoc
<https://github.com/caltechads/sphinxcontrib-jsonglobaltoc>`_.   This extension
extends :py:class:`JSONHTMLBuilder` from ``sphinxcontrib-serializinghtml`` to
add a ``globaltoc`` key to each ``.fjson`` file produced.  ``globaltoc``
contains the HTML for the global table of contents for the entire set of
documentation.  This allows django-sphinx-hosting to more reliably build your
navigation.

.. code-block:: python

    extensions = [
        'sphinx_rtd_theme',
        'sphinx_json_globaltoc'
        ...
    ]
