.. _api:


Developer Interface
===================

.. module:: ldap_faker

This part of the documentation covers all the classes and functions that make up ``python-ldap-faker``.

Unittest Support
----------------

.. autoclass:: LDAPFakerMixin
    :inherited-members:
    :undoc-members:

.. autoclass:: LDAPCallRecord
    :members:

.. autoclass:: CallHistory
    :inherited-members:
    :undoc-members:


python-ldap replacements
------------------------

.. autoclass:: FakeLDAP
    :inherited-members:
    :undoc-members:

.. autoclass:: FakeLDAPObject
    :inherited-members:
    :undoc-members:


LDAP Server like objects
------------------------

.. autoclass:: LDAPServerFactory
    :inherited-members:
    :undoc-members:

.. autoclass:: ObjectStore
    :inherited-members:
    :undoc-members:

.. autoclass:: OptionStore
    :inherited-members:
    :undoc-members:


Hook management
---------------

.. autodata:: hooks

.. autoclass:: Hook
    :inherited-members:
    :undoc-members:

.. autoclass:: HookDefinition
    :inherited-members:
    :undoc-members:

.. autoclass:: HookRegistry
    :inherited-members:
    :undoc-members:


Type Aliases
------------

.. autodata:: ldap_faker.types.LDAPOptionValue

.. autodata:: ldap_faker.types.LDAPData

.. autodata:: ldap_faker.types.LDAPRecord

.. autodata:: ldap_faker.types.LDAPSearchResult

.. autodata:: ldap_faker.types.ModList

.. autodata:: ldap_faker.types.AddModList

.. autodata:: ldap_faker.types.LDAPFixtureList


