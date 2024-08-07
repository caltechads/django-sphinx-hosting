=====================
django-sphinx-hosting
=====================

.. toctree::
   :caption: Overview
   :hidden:

   overview/authorization
   overview/packaging
   overview/authoring
   overview/importing
   overview/api

.. toctree::
   :caption: Runbook
   :hidden:

   runbook/main

.. toctree::
   :caption: Reference
   :hidden:

   api/models.rst
   api/forms.rst
   api/importers.rst
   api/widgets.rst
   api/rest_api.rst



Current version is |release|.

This reusable Django application provides models, views, permissions, REST API
endpoints and management commands for making a private Sphinx documentation
hosting platform.

This is useful for when you want Sphinx documentation for your internal software
projects, but you do not want that documentation do be shared with a
third-party.


Installation
------------

To install from PyPI::

   pip install django-sphinx-hosting

If you want, you can run the tests::

   python -m unittest discover


Features
--------

* Users must be authenticated to view docs
* Multiple levels of privileges within the system based on Django authentication
* Manage multiple versions of your docs per project
* Automatically build and display navigation for each version of your documentaion
* Renders all documentation published within with a consistent theme
* Tag projects with classifiers to refine searching and filtering
* Search across all projects
* Use REST API to programmatically interact with the system.  Useful for
  integrating into a CI/CD system


Configuration
-------------

Update ``INSTALLED_APPS``
^^^^^^^^^^^^^^^^^^^^^^^^^

As with most Django applications, you should add ``django-sphinx-hosting`` and
its key dependencies to the ``INSTALLED_APPS`` within your settings file
(usually ``settings.py``).

Example:

.. code-block:: python

   INSTALLED_APPS = [
      'django.contrib.admin',
      'django.contrib.auth',
      'django.contrib.contenttypes',
      'django.contrib.messages',
      'django.contrib.sessions',
      'django.contrib.sites',

      # ---------- add these ----------------
      'rest_framework',
      'rest_framework.authtoken',
      'django_filters',
      'drf_spectacular',
      'crispy_forms',
      'crispy_bootstrap5',
      'haystack',
      'academy_theme',
      'wildewidgets',
      'sphinx_hosting',
      'sphinx_hosting.api'
      # -------- done add these -------------

      # Then your usual apps...
      'blog',
   ]


Configure ``django-sphinx-hosting`` itself
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For ``django-sphinx-hosting`` itself, you'll typically want to add a
``SPHINX_HOSTING_SETTINGS`` dict to localize django-sphinx-hosting to your
organization.

Full example:

.. code-block:: python

   SPHINX_HOSTING_SETTINGS = {
      'LOGO_IMAGE': 'core/images/my-org-logo.png',
      'LOGO_WIDTH': '75%',
      'LOGO_URL': 'https://www.example.com',
      'SITE_NAME': 'MyOrg Documentation'
      'EXCLUDE_FROM_LATEST': ['*.dev*', '*.beta*']
   }

``LOGO_IMAGE``
   A Django filesystem path to the image you want to use for the logo at the top
   of the navigation sidebar.

``LOGO_WIDTH``
   Any valid CSS width specifier.  This will be applied to the ``LOGO_IMAGE``.

``LOGO_URL``
   When a user clicks the ``LOGO_IMAGE``, they'll be sent to this URL.

``SITE_NAME``
   This will be used in the HTML title tags for each page, and wil be used as
   the ``alt`` tag for the ``LOGO_IMAGE``.

``EXCLUDE_FROM_LATEST``
   This is a list of glob patterns to apply to version numbers.  If the version
   number matches any of these patterns, it will not be marked as latest in the
   database and will not be indexed in the search engine.  The default list of
   patterns is ``['*.dev*', '*.alpha*', '*.beta*', '*.rc*']``.

Configure django-wildewidgets
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All HTML in ``django-sphinx-hosting`` is generated by `django-wildewidgets
<https://github.com/caltechads/django-wildewidgets>`_ widgets.  We use the
`django-theme-academy <https://github.com/caltechads/django-theme-academy>`_ to
provide the HTML boilerplate to house the widget output, and
`django-crispy-forms
<https://github.com/django-crispy-forms/django-crispy-forms>`_ for our form
rendering.

Add this code to your ``settings.py`` to configure them properly:

.. code-block:: python

   # crispy-forms
   # ------------------------------------------------------------------------------
   CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
   CRISPY_TEMPLATE_PACK = 'bootstrap5'

   # django-theme-academy
   # ------------------------------------------------------------------------------
   ACADEMY_THEME_SETTINGS = {
      # Header
      'APPLE_TOUCH_ICON': 'core/images/apple-touch-icon.png',
      'FAVICON_32': 'core/images/favicon-32x32.png',
      'FAVICON_16': 'core/images/favicon-16x16.png',
      'FAVICON': 'core/images/favicon.ico',
      'SITE_WEBMANIFEST': 'core/images/site.webmanifest',

      # Footer
      'ORGANIZATION_LINK': 'https://github.com/caltechads/django-sphinx-hosting',
      'ORGANIZATION_NAME': 'Sphinx Hosting',
      'ORGANIZATION_ADDRESS': '123 Main Street, Everytown, ST',
      'COPYRIGHT_ORGANIZATION': 'Sphinx Hosting',
      'FOOTER_LINKS': [
         ('https://example.com', 'Organization Home'),
         ('https://example.com/documents/privacy.pdf', "Privacy Policy")
      ]
   }

   # django-wildewidgets
   # ------------------------------------------------------------------------------
   WILDEWIDGETS_DATETIME_FORMAT = "%Y-%m-%d %H:%M %Z"

For ``ACADEMY_THEME_SETTINGS``, localize to your organization by updating all the settings
appropriately.

``FAVICON_*``, ``APPLE_TOUCH_ICON`` and ``SITE_WEBMANIFEST``
   Set these to the Django filesystem path to the files you want to use.

``FOOTER_LINKS``
   Add links to the footer by listing 2-tuples of  ``("__URL__", "__LABEL__")``


Configure Haystack
^^^^^^^^^^^^^^^^^^

We use `django-haystack <https://github.com/django-haystack/django-haystack>`_
to support our documentation search feature, but it is up to you what specific
backend you want to configure.  See `Haystack: Configuration
<https://django-haystack.readthedocs.io/en/master/tutorial.html#configuration>`_
for instructions on how to configure Haystack for different backends.

Here is example ``settings.py`` code for using Elasticsearch 7.x as our search backend:

.. code-block:: python

   HAYSTACK_CONNECTIONS = {
      'default': {
         'ENGINE': 'haystack.backends.elasticsearch7_backend.Elasticsearch7SearchEngine',
         'URL': 'http://sphinx-hosting-search.example.com:9200/',
         'INDEX_NAME': 'sphinx_hosting',
      },
   }


.. _configure-django-rest-framework:

Configure Django REST Framework
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To make the ``django-sphinx-hosting`` API work, add this code to your ``settings.py``:

.. code-block:: python

   # djangorestframework
   # ------------------------------------------------------------------------------
   REST_FRAMEWORK = {
      # https://www.django-rest-framework.org/api-guide/parsers/#setting-the-parsers
      'DEFAULT_PARSER_CLASSES': ('rest_framework.parsers.JSONParser',),
      # https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication
      'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework.authentication.TokenAuthentication',),
      # https://django-filter.readthedocs.io/en/master/guide/rest_framework.html
      'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
      # https://www.django-rest-framework.org/api-guide/pagination/#limitoffsetpagination
      'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
      # https://github.com/tfranzel/drf-spectacular
      'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
      'PAGE_SIZE': 100,
   }

   # drf-spectacular
   # ------------------------------------------------------------------------------
   # https://drf-spectacular.readthedocs.io/en/latest/settings.html
   SPECTACULAR_SETTINGS = {
      'SCHEMA_PATH_PREFIX': r'/api/v1',
      'SERVERS': [
         {
               'url': 'https://localhost',
               'description': 'Django Sphinx Hosting'
         }
      ],
      'TITLE': 'YOUR_SITE_NAME'
      'VERSION': __version__,
      'DESCRIPTION': """__YOUR_DESCRIPTION__HERE"""
   }


For ``DEFAULT_AUTHENTICATION_CLASSES``, use whatever authentication class you
want -- we're just using ``TokenAuthentication`` here as an example.  For the rest
of the settings, you'll need at least what we've detailed above, but feel free to add
to them if you have additional API views you need to support in your own application
code.

Update your top-level urlconf
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from django.urls import path, include

   from sphinx_hosting import urls as sphinx_hosting_urls
   from sphinx_hosting.api import urls as sphinx_hosting_api_urls
   from wildewidgets import WildewidgetDispatch

   urlpatterns = [
      path('/docs/', include(sphinx_hosting_urls, namespace='sphinx_hosting')),
      path('/docs/wildewidgets_json', WildewidgetDispatch.as_view(), name='wildewidgets_json'),
      path('api/v1/', include(sphinx_hosting_api_urls, namespace='sphinx_hosting_api')),
   ]



