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
3. Ensure your changes work by running the demo app in ``sandbox``.
4. Update the documentation to reflect your changes.
5. Commit changes to your branch.
6.


Preconditions for working on django-sphinx-hosting
--------------------------------------------------

We expect you to use a python virtual environment to hold the python
requirements for building the Sphinx documentation.

To use ``pyenv`` to make your virtualenv:

.. code-block:: shell

   $ cd django-sphinx-hosting
   $ pyenv virtualenv 3.10.6 django-sphinx-hosting
   $ pyenv local django-sphinx-hosting
   $ pip install --upgrade pip wheel

After that please install libraries required for working with the code and
building the documentation.

.. code-block:: shell

   $ pip install -r requirements.txt
