# django-sphinx-hosting

**Documentation**: [django-sphinx-hosting.readthedocs.org](https://django-sphinx-hosting.readthedocs.org)

This reusable Django application provides models, views, permissions, REST API
endpoints and management commands for making a private Sphinx documentation
hosting platform.

This is useful for when you want Sphinx documentation for your internal software
projects, but that is too sensitive to be shared with a third party.

## Features

* Users must be authenticated to view docs
* Multiple levels of privileges within the system based on Django authentication
* Manage multiple versions of your docs per project
* Automatically build and display navigation for each version of your documentaion
* Renders all documentation published within with a consistent theme
* Tag projects with classifiers to refine searching and filtering
* Search across all projects
* Use REST API to programmatically interact with the system.  Useful for
  integrating into a CI/CD system

## Installation and Configuration

See the [documentation](https://django-sphinx-hosting.readthedocs.org) for how
to install and configure `django-sphinx-hosting` in your Django project.
