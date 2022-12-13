.. _api:


Developer Interface
===================

Models
------

.. module:: sphinx_hosting.models

This part of the documentation covers all the models provided by ``django-sphinx-hosting``.

Projects
^^^^^^^^

.. autoclass:: Project
    :members:
    :undoc-members:

.. autoclass:: Version
    :members:
    :undoc-members:

.. autoclass:: SphinxPage
    :members:
    :undoc-members:

.. autoclass:: SphinxImage
    :members:
    :undoc-members:


Widgets
-------

This part of the documentation covers all the reusable `django-wildewidgets
<https://github.com/caltechads/django-wildewidgets>`_ widgets provided by
``django-sphinx-hosting``.

.. module:: sphinx_hosting.wildewidgets

Basic Widgets
^^^^^^^^^^^^^

.. autoclass:: Datagrid
    :members:

.. autoclass:: DatagridItem
    :members:

Navigation
^^^^^^^^^^

.. autoclass:: SphinxHostingMenu
    :members:

.. autoclass:: SphinxHostingBreadcrumbs
    :members:

Modals
^^^^^^

.. autoclass:: ProjectCreateModalWidget
    :members:

.. autoclass:: ProjectTableWidget
    :members:

.. autoclass:: ProjectTable
    :members:


Importers
---------

.. module:: sphinx_hosting.importers

.. autoclass:: SphinxPackageImporter
    :members: