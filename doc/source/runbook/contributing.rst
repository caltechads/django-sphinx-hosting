.. _runbook__contributing:

Contributing
============

Instructions for contributors
-----------------------------

Make a clone of the github repo:

.. code-block:: shell

    $ git clone https://github.com/caltechads/django-sphinx-hosting


Workflow is pretty straightforward:

1. Make sure you are reading the latest version of this document.
2. Setup your machine with the required development environment
3. Make your changes.
4. Ensure your changes work by running the demo app in ``sandbox``.
5. Update the documentation to reflect your changes.
6. Commit changes to your branch.


Preconditions for working on django-sphinx-hosting
--------------------------------------------------

Python environment
^^^^^^^^^^^^^^^^^^

The Amazon Linux 2 base image we use here for our sandbox service has Python
3.14.x, so we'll want that in our virtualenv.

Here is an example of using ``pyenv`` to make your virtualenv:

.. code-block:: shell

   $ cd django-sphinx-hosting
   $ uv venv -p 3.14
   $ uv sync --dev

Docker
^^^^^^

Running the local docker stack
------------------------------

Build the Docker image
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    $ cd sandbox
    $ make build

Run the service and initialize the database
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The first time you run the stack only, do:

.. code-block:: shell

    $ docker-compose up mysql

Wait for the database to initialize itself, then stop the mysql container by
doing ^C.

.. code-block:: shell

    $ make dev

This will start the service and apply alll the Django database migrations.

Getting to the demo in your browser
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Browse to https://localhost to get to the demo application.

There are 3 users available:

* ``admin`` with password ``testy``: This user is in the ``Administrators``
  Django group.  This user can do anything.
* ``editor`` with password ``testy``: This user is in the ``Project Managers``
  and ``Version Managers`` Django groups.  This user can do anything except
  manage ``Classifiers``.
* ``viewer`` with password ``testy``: This user is in no groups.  This user can
  only view the documentation.

The ``demo`` container is running with ``gunicorn`` reload-on-change enabled, so
you may edit files and see the changes reflected in the browser witout having
to restart the container.
