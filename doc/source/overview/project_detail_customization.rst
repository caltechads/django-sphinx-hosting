Project Detail Customization
============================

``django-sphinx-hosting`` lets host Django projects extend the
``ProjectDetailView`` layout without subclassing or replacing package views.
Use ``PROJECT_DETAIL_LAYOUT_BUILDERS`` when you want to append new blocks to
the main content area or use the live ``WidgetListLayout`` API to add sidebar
actions and widgets.


When to use this hook
---------------------

Use ``PROJECT_DETAIL_LAYOUT_BUILDERS`` when a host project needs to:

* append one or more widgets to the project detail page
* add sidebar links or form buttons that integrate with surrounding systems
* add sidebar widgets or other actions using the exposed layout object

Builders are append-only for the main content area. The package adds its
built-in project detail widgets first, then runs your builders in list order.


Builder contract
----------------

Configure one or more dotted-path callables in ``SPHINX_HOSTING_SETTINGS``.

.. code-block:: python

   def extend_project_detail_layout(*, request, user, project, layout, view) -> None:
      ...

The builder arguments are:

``request``
   The current Django request.

``user``
   The authenticated user for the request.

``project``
   The ``sphinx_hosting.models.Project`` shown on the page.

``layout``
   The live ``wildewidgets.WidgetListLayout`` instance. Mutate this object in
   place to append widgets or change the sidebar.

``view``
   The active ``sphinx_hosting.views.ProjectDetailView`` instance.


Example host-project builder
----------------------------

.. code-block:: python

   # myproject/core/wildewidgets.py
   from wildewidgets import Block, CardWidget

   def extend_project_detail_layout(*, request, user, project, layout, view) -> None:
      del request, user, view
      layout.add_widget(
         CardWidget(
            title="Ecosystem Integrations",
            icon="boxes",
            widget=Block(
               f"Extra project-specific details for {project.title} can go here."
            ),
         )
      )
      layout.add_sidebar_link_button(
         "Support Runbook",
         f"/support/projects/{project.machine_name}/",
         color="teal",
      )
      layout.add_sidebar_form_button(
         "Sync Metadata",
         "/integrations/sync-project/",
         color="outline-primary",
         data={"project": project.pk},
      )

.. code-block:: python

   SPHINX_HOSTING_SETTINGS = {
      "PROJECT_DETAIL_LAYOUT_BUILDERS": [
         "myproject.core.wildewidgets.extend_project_detail_layout",
      ],
   }


Available layout APIs
---------------------

The ``layout`` object is the actual ``WidgetListLayout`` used by
``ProjectDetailView``. Common extension methods include:

* ``layout.add_widget(...)``
* ``layout.add_sidebar_link_button(...)``
* ``layout.add_sidebar_form_button(...)``
* ``layout.add_sidebar_widget(...)``
* ``layout.add_sidebar_bare_widget(...)``

This means host projects can append ``WidgetListLayout``-compatible blocks to
the main column and use the full public sidebar API without reimplementing the
view.
