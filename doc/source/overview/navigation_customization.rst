Navigation Customization
========================

``django-sphinx-hosting`` ships with a default sidebar, but host projects can
extend or replace menu behavior without forking package views.


Static menu items
-----------------

Use ``EXTRA_MENU_ITEMS`` when a link should always be present.

.. code-block:: python

   SPHINX_HOSTING_SETTINGS = {
      "EXTRA_MENU_ITEMS": [
         {
            "text": "REST API",
            "icon": "diagram-3",
            "url": "/api/v1/schema/swagger-ui/",
         },
      ]
   }

``icon`` values should be Bootstrap Icons names.


Conditional menu items
----------------------

Use ``MENU_ITEM_BUILDERS`` when links depend on request-time state.

.. code-block:: python

   # myproject/core/navigation.py
   from typing import Any

   def build_menu_items(*, request, user, menu) -> dict[str, Any] | None:
      if not user.is_staff:
         return None
      return {"text": "Admin", "icon": "shield", "url": "/admin/"}

.. code-block:: python

   SPHINX_HOSTING_SETTINGS = {
      "MENU_ITEM_BUILDERS": ["myproject.core.navigation.build_menu_items"]
   }

Builder return values may be ``None``, one ``MenuItem``/dict, or an iterable of
``MenuItem``/dict entries.  Exceptions are propagated so configuration bugs are
visible in logs and error monitoring.


Full sidebar override
---------------------

Use ``NAVBAR_CLASS`` to replace the entire sidebar class while keeping package
views unchanged.

.. code-block:: python

   # myproject/core/wildewidgets.py
   from sphinx_hosting.wildewidgets import SphinxHostingSidebar

   class MainMenu(SphinxHostingSidebar):
      pass

.. code-block:: python

   SPHINX_HOSTING_SETTINGS = {
      "NAVBAR_CLASS": "myproject.core.wildewidgets.MainMenu"
   }

The demo project in ``sandbox/demo/settings.py`` includes a complete working
example using ``EXTRA_MENU_ITEMS``, ``MENU_ITEM_BUILDERS``, and ``NAVBAR_CLASS``.
