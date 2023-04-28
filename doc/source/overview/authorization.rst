.. _overview_authorization:

User authorization
==================

``django-sphinx-hosting`` uses Django model permissions to restrict access to
the various views within it.

We provide Django groups to which you can assign your users to grant them
different levels of privileges.  Users who are assigned to none of these groups
are ``Viewers``: they can search and read the documentation sets within, but
they cannot create, modify or delete anything.

Administrators
--------------

Users in the ``Administrators`` group have full privileges within the system.

* Create, edit, delete :py:class:`sphinx_hosting.models.Project` objects
* Create, edit, delete :py:class:`sphinx_hosting.models.Version` objects
* Create, edit, delete :py:class:`sphinx_hosting.models.Classifier` objects

Editors
-------

Users in the ``Editors`` group can work with projects and versions but have no
rights to manage :py:class:`sphinx_hosting.models.Classifier` objects.

* Create, edit, delete :py:class:`sphinx_hosting.models.Project` objects
* Create, edit, delete :py:class:`sphinx_hosting.models.Version` objects


Project Managers
----------------

Users in the ``Project Managers`` group can only manage projects.


Version Managers
----------------

Users in the ``Version Managers`` group can only manage versions.

Classifier Managers
-------------------

Users in the ``Classifier Managers`` group can only manage classiiers.