.. _overview_api:

The django-sphinx-hosting REST API
==================================

``django-sphinx-hosting`` provides a REST API for interacting with the the application in
a programmatic way. The API is implemented using `Django REST Framework
<https://www.django-rest-framework.org/>`_.

See :ref:`configure-django-rest-framework` for instructions on how generally to
configure your ``settings.py`` file to use DRF for our API.

How to reach the API
--------------------

The API is reachable at the following path of your install: ``/api/v1/``.  See
:doc:`/api/rest_api` for the description of all endpoints.

Authentication
--------------

It's up to you to provide an authentication mechanism for the API via the
``REST_FRAMEWORK`` setting in your ``settings.py`` file.  ``django-sphinx-hosting``
will use whatever you provide for the ``DEFAULT_AUTHENTICATION_CLASSES`` setting.

See the `Django REST Framework: Authentication
<https://www.django-rest-framework.org/api-guide/authentication/>`_  for more
information on how to configure authentication for DRF.

Example
^^^^^^^

Here's an example of how to configure the API to use Token based authentication:

.. code-block:: python

    INSTALLED_APPS = [
        ...
        'rest_framework.authtoken',
        ...
    ]

    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework.authentication.TokenAuthentication',),
        # https://www.django-rest-framework.org/api-guide/parsers/#setting-the-parsers
        'DEFAULT_PARSER_CLASSES': ('rest_framework.parsers.JSONParser',),
        # https://django-filter.readthedocs.io/en/master/guide/rest_framework.html
        'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    }

.. note::
    We always need at least the ``DEFAULT_PARSER_CLASSES`` setting and the
    ``DEFAULT_FILTER_BACKENDS`` listed above for the API to work at all, regardless
    of the authentication mechanism you choose, so be sure to include them.

Then migrate the database to create the ``Token`` model:

.. code-block:: bash

    $ python manage.py migrate

And then create a token for your user:

.. code-block:: bash

    $ python manage.py drf_create_token <username>

To use this token, you must provide it in the ``Authorization`` header of your
requests.  Example:

.. code-block:: bash

    $ curl -X GET \\
        -H 'Accept: application/json; indent=4' \\
        -H 'Authorization: Token __THE_TOKEN__' \\
        --insecure \\
        --verbose \\
        https://localhost/api/v1/projects/

Authoriztion
------------

The API endpoints all require that the user be authenticated.  All users
have read-only access to all API endpoints, but for write access, they must
be in the appropriate group or groups from :doc:`/overview/authorization`.