# Graph Report - django-sphinx-hosting  (2026-08-19)

## Corpus Check
- 137 files · ~71,581 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1430 nodes · 2871 edges · 152 communities (98 shown, 54 thin omitted)
- Extraction: 77% EXTRACTED · 23% INFERRED · 0% AMBIGUOUS · INFERRED: 650 edges (avg confidence: 0.56)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `50f05055`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- SphinxPackageImporter
- .__init__
- check_napoleon_gate.py
- Version
- test_project_detail_extensibility.py
- ProjectReadonlyUpdateForm
- test_navigation_extensibility.py
- .__init__
- wildewidgets/search.py
- SearchNote
- sphinx_hosting/views.py
- Classifier
- AGENTS.md
- ClassifierNode
- APIUser
- Version
- .get_content
- test_unified_search_integration.py
- SphinxGlobalTOCHTMLProcessor
- ProjectRelatedLink
- SphinxHostingBreadcrumbs
- Project
- demo/settings.py
- SphinxHostingMainMenu
- ClassifierFilterBlock
- SearchNoteDetailView
- SearchNoteIndex
- test_search_note_integration.py
- test_unified_search_extensibility.py
- Project
- validators.py
- ProjectTable
- test_host_project_can_extend_navigation_without_losing_defaults
- .get_content
- test_project_detail_customization_integration.py
- .get_queryset
- ProjectRelatedLinksWidget
- render_search_note_result
- SPHINX_HOSTING_SETTINGS
- navigation.py
- django-sphinx-hosting
- Global Table of Contents
- seed_search_notes.py
- SearchNoteCreateView
- .__init__
- django-sphinx-hosting REST API
- extend_project_detail_layout
- SphinxHostingSidebar
- 0003_load_search_notes_fixture.py
- .__init__
- .save
- GlobalSearchFormWidget
- SEARCH_RESULT_RENDERERS
- _normalize_builder_result
- Command
- 0010_add_groups.py
- .__call__
- wait-for-it.sh
- 16x16 Favicon
- 0015_migrate_to_latest_version_field.py
- sphinx_rtd_theme Required Theme
- Android Chrome 512x512 App Icon
- Apple Touch Icon
- Favicon 32x32
- sphinxdocument_url
- SphinxHostingAppConfig
- Sphinx Hosting Logo
- PageTreeNode
- Demo Users admin editor viewer
- Android Chrome 192x192 Icon
- 0002_load_fixture.py
- 0003_api_group.py
- 0005_api_user_permissions.py
- SphinxHostingApiAppConfig
- 0007_load_classifiers.py
- sandbox/demo Django Project
- California Institute of Technology
- CoreConfig
- Migration
- Migration
- UsersConfig
- Read the Docs Sphinx Build
- Napoleon Documentation Contract
- release.sh
- GlobalSearchForm
- MachineNameField (form fields)
- sphinx_image_upload_to
- ClassifierFilterBlock
- Contributing
- django-sphinx-hosting
- collectstatic.sh
- entrypoint.sh
- restart_gunicorn.sh
- test-runner.sh
- test-runner-warnings.sh
- users/migrations/0001_initial.py
- 0002_original_html.py
- 0003_globaltoc.py
- 0004_next_page_FK.py
- 0005_orig_global_toc.py
- 0008_Version_archived.py
- 0009_SphinxPage_searchable.py
- 0012_project_relatedlinks.py
- 0013_projectrelatedlink_url_to_uri.py
- 0014_latest_version_as_field.py
- 0016_project_last_version_alter.py
- 0017_alter_sphinxpage_body_and_more.py
- Sphinx 6.2.1
- sphinxcontrib-django
- ProjectCreateForm
- ProjectReadonlyUpdateForm
- ProjectUpdateForm
- ClassifierFilterForm
- MENU_ITEM_BUILDERS
- NAVBAR_CLASS
- PagedSearchLayout
- ProjectDetailWidget
- ProjectTableWidget
- SearchResultsProjectFacet
- SphinxHostingBreadcrumbs
- SphinxHostingMainMenu
- SphinxPageLayout
- Classifier Managers
- import_docs Management Command
- caltechads/django-sphinx-hosting
- Django
- playwright

## God Nodes (most connected - your core abstractions)
1. `Project` - 80 edges
2. `Version` - 77 edges
3. `SphinxPackageImporter` - 63 edges
4. `SphinxPage` - 60 edges
5. `SearchNote` - 43 edges
6. `ProjectRelatedLink` - 43 edges
7. `Classifier` - 41 edges
8. `ProjectReadonlyUpdateForm` - 30 edges
9. `VersionUploadForm` - 29 edges
10. `GlobalSphinxPageSearchView` - 29 edges

## Surprising Connections (you probably didn't know these)
- `django-sphinx-hosting` --semantically_similar_to--> `django-sphinx-hosting`  [INFERRED] [semantically similar]
  README.md → doc/source/index.rst
- `Multiple Documentation Versions Per Project` --semantically_similar_to--> `Version`  [INFERRED] [semantically similar]
  README.md → doc/source/api/models.rst
- `sandbox/demo Django Project` --semantically_similar_to--> `sandbox Demo Application`  [INFERRED] [semantically similar]
  AGENTS.md → doc/source/runbook/contributing.rst
- `REST API` --semantically_similar_to--> `django-sphinx-hosting REST API`  [INFERRED] [semantically similar]
  README.md → doc/source/overview/api.rst
- `Search Across All Projects` --semantically_similar_to--> `Unified Search`  [INFERRED] [semantically similar]
  README.md → doc/source/overview/unified_search.rst

## Import Cycles
- 3-file cycle: `sphinx_hosting/fields.py -> sphinx_hosting/templatetags/sphinx_hosting.py -> sphinx_hosting/models.py -> sphinx_hosting/fields.py`

## Hyperedges (group relationships)
- **Sphinx documentation import pathways** — doc_source_overview_importing_json_tarball, doc_source_overview_importing_upload_form, doc_source_overview_importing_api_version_import, doc_source_overview_importing_import_docs_command, doc_source_api_importers_sphinxpackageimporter [EXTRACTED 1.00]
- **Django privilege groups** — doc_source_overview_authorization_viewers, doc_source_overview_authorization_administrators, doc_source_overview_authorization_editors, doc_source_overview_authorization_project_managers, doc_source_overview_authorization_version_managers, doc_source_overview_authorization_classifier_managers [EXTRACTED 1.00]
- **Host-project extension hooks** — doc_source_index_extra_menu_items, doc_source_index_menu_item_builders, doc_source_index_navbar_class, doc_source_index_project_detail_layout_builders, doc_source_index_search_result_renderers [EXTRACTED 1.00]
- **Demo Docker runtime stack** — sandbox_docker_compose_demo, sandbox_docker_compose_mysql, sandbox_docker_compose_opensearch [EXTRACTED 1.00]
- **OpenAPI core documentation resources** — schema_v1_classifier, schema_v1_project, schema_v1_version, schema_v1_sphinxpage, schema_v1_sphinximage, schema_v1_projectrelatedlink [EXTRACTED 1.00]
- **Academy theme template shell** — sandbox_demo_core_templates_core_intermediate_intermediate, sandbox_demo_users_templates_users_intermediate_intermediate, sphinx_hosting_templates_sphinx_hosting_base_base [INFERRED 0.85]
- **Demo App Branding** — sandbox_demo_core_static_core_images_android_chrome_192x192_android_chrome_icon, sandbox_demo_core_static_core_images_android_chrome_192x192_sphinx_lettermark, sandbox_demo_core_static_core_images_android_chrome_192x192_pwa_homescreen_icon, sandbox_demo_core_static_core_images_android_chrome_192x192_circular_lettermark_logo [INFERRED 0.75]
- **Sphinx-style S on Blue Disc Brand Mark** — sandbox_demo_core_static_core_images_android_chrome_512x512_icon, sandbox_demo_core_static_core_images_android_chrome_512x512_serif_s, sandbox_demo_core_static_core_images_android_chrome_512x512_blue_circle_badge [EXTRACTED 1.00]
- **Demo iOS Home-Screen Branding** — sandbox_demo_core_static_core_images_apple_touch_icon_apple_touch_icon, sandbox_demo_core_static_core_images_apple_touch_icon_sphinx_s_monogram, sandbox_demo_core_static_core_images_apple_touch_icon_ios_home_screen_icon [INFERRED 0.75]
- **Site Chrome Identity** — sandbox_demo_core_static_core_images_favicon_16x16_favicon, sandbox_demo_core_static_core_images_favicon_16x16_sphinx_lettermark, sandbox_demo_core_static_core_images_favicon_16x16_blue_circular_badge, sandbox_demo_core_static_core_images_favicon_16x16_browser_tab_icon [INFERRED 0.75]
- **Demo Site Brand Mark** — sandbox_demo_core_static_core_images_favicon_32x32_favicon, sandbox_demo_core_static_core_images_favicon_32x32_circular_badge, sandbox_demo_core_static_core_images_favicon_32x32_s_monogram [EXTRACTED 1.00]
- **Sphinx Hosting Brand Lockup** — sphinx_hosting_static_sphinx_hosting_images_logo_sphinx_icon, sphinx_hosting_static_sphinx_hosting_images_logo_wordmark, sphinx_hosting_static_sphinx_hosting_images_logo_sphinx_hosting_logo [EXTRACTED 1.00]

## Communities (152 total, 54 thin omitted)

### Community 0 - "SphinxPackageImporter"
Cohesion: 0.07
Nodes (65): action, BufferedReader, Exception, IO, Response, AddVersionPermission, ChangeProjectPermission, APIView (+57 more)

### Community 1 - ".__init__"
Cohesion: 0.06
Nodes (29): Generate the set of widgets for this page. Returns: A populated page layout, BasicModelTable, CardWidget, QuerySet, WidgetListLayoutHeader, A :py:class:`wildewidgets.CardWidget` that gives our…, Displays a `dataTable <https://datatables.net>`_ of our…, Gives a :py:class:`wildewidget.Datagrid` type overview of information about… (+21 more)

### Community 2 - "check_napoleon_gate.py"
Cohesion: 0.07
Nodes (45): AsyncFunctionDef, _check_file(), _check_function_doc(), _constructor_has_args(), _first_doc_line(), _function_has_args(), _function_has_keyword_args(), _function_uses_return_or_yield() (+37 more)

### Community 3 - "Version"
Cohesion: 0.06
Nodes (42): django-haystack, django-theme-academy, django-wildewidgets, Django REST Framework, drf-spectacular, elasticsearch, mysqlclient, sphinxcontrib-openapi (+34 more)

### Community 4 - "test_project_detail_extensibility.py"
Cohesion: 0.09
Nodes (34): BaseProjectUpdateView, build_project_detail_layout(), build_project_update_layout(), clear_builder_state(), DummyUser, django_db, fixture, override_settings (+26 more)

### Community 5 - "ProjectReadonlyUpdateForm"
Cohesion: 0.13
Nodes (30): BaseProjectDetailView, MessageMixin, NavbarMixin, SearchView, ProjectReadonlyUpdateForm, ProjectRelatedLinkCreateForm, ProjectUpdateForm, The form we use to on the :py:class:`sphinx_hosting.views.ProjectDetailView` to… (+22 more)

### Community 6 - "test_navigation_extensibility.py"
Cohesion: 0.08
Nodes (32): Navbar, _build_menu(), builder_admin(), _capture_built_items(), DummyRequest, DummyUser, NotANavbar, MenuItem (+24 more)

### Community 7 - ".__init__"
Cohesion: 0.13
Nodes (16): Row, Block, CardWidget, Return the Javascript that will be executed when the "Permalink" button is…, The body of the page. The body as stored in the model is actually a Django…, Draws the in-page navigation -- the header hierarchy. Args: page: the…, The title block for a :py:class:`sphinx_hosting.models.SphinxPage` page. Args:…, Draws the "Previous Page", Parent Page and Next Page buttons that are found at… (+8 more)

### Community 8 - "wildewidgets/search.py"
Cohesion: 0.07
Nodes (41): Widget, Build the unified-search page layout. Returns: The populated unified-search…, FacetBlock, Header, PagedSearchLayout, PagedSearchResultsBlock, Block, HorizontalLayoutBlock (+33 more)

### Community 9 - "SearchNote"
Cohesion: 0.11
Nodes (15): Meta, Form used to create and update demo ``SearchNote`` records. Keyword Args:…, Configure crispy layout and sorted relation choices for the form. Args: *args:…, SearchNoteForm, Meta, TimeStampedModel, Demo-only searchable content used to exercise unified global search.…, Return the visible label for this note. Returns: The note title. (+7 more)

### Community 10 - "sphinx_hosting/views.py"
Cohesion: 0.12
Nodes (13): Model, QuerySet, Search index for SphinxPage model., Return the SphinxPage model class., Prepare the classifiers for the SphinxPage. Args: obj: The SphinxPage object…, Used when the entire index for model is updated. Keyword Args: using: The alias…, Remove all pages for a version from the index. Args: version: The version whose…, Reindex all pages for a project. This happens when we get a new latest_version… (+5 more)

### Community 11 - "Classifier"
Cohesion: 0.08
Nodes (30): BaseCreateView, BaseFormView, BaseUpdateView, FormInvalidMessageMixin, FormValidMessageMixin, PermissionRequiredMixin, ProjectCreateForm, The form we use to force a version to be the latest version of a project. (+22 more)

### Community 12 - "AGENTS.md"
Cohesion: 0.17
Nodes (11): AGENTS.md, Architecture (Required), AWS Interaction, Documentation Contract (Required), graphify, Implementation Priority (Required), Post-Implementation Quality Gate (Required), Project Structure (Mandatory) (+3 more)

### Community 13 - "ClassifierNode"
Cohesion: 0.12
Nodes (15): Command, BaseCommand, Tree, **Usage**: ``./manage.py print_classifier_tree`` Print the…, Parse the tree of :py:class:`sphinx_hosting.models.ClassifierNode` objects we…, TreePrinter, ClassifierNode, Given our classifiers, which are ``::`` separated lists of terms like:: Section… (+7 more)

### Community 14 - "APIUser"
Cohesion: 0.10
Nodes (15): Command, BaseCommand, Command, BaseCommand, Migration, APIUser, APIUserManager, finalize_api_user() (+7 more)

### Community 15 - "Version"
Cohesion: 0.08
Nodes (25): deconstructible, MachineNameField, A :py:class:`django.forms.SlugField` that also allows "." characters. "." is…, PageTreeNode, A data structure to temporarily hold relationships between…, Migration, Migration, ClassifierManager (+17 more)

### Community 16 - ".get_content"
Cohesion: 0.12
Nodes (16): Widget, Build the project update layout and apply host-project extensions. Returns: The…, Widget, ProjectClassifierSelectorWidget, ProjectDetailWidget, ProjectInfoWidget, ProjectVersionsTableWidget, CrispyFormWidget (+8 more)

### Community 17 - "test_unified_search_integration.py"
Cohesion: 0.26
Nodes (11): clear_search_backend(), _create_search_fixture(), _index_instance(), fixture, Refresh the active Haystack backend when the backend exposes a refresh API.…, Index one model instance into the active Haystack backend. Args: instance: The…, _refresh_search_backend(), test_unified_search_classifier_facet_filters_built_in_and_host_hits() (+3 more)

### Community 18 - "SphinxGlobalTOCHTMLProcessor"
Cohesion: 0.05
Nodes (30): HtmlElement, Command, ArgumentParser, BaseCommand, **Usage**: ``./manage.py print_globaltoc <project_machine_name> <version…, Command, ArgumentParser, BaseCommand (+22 more)

### Community 19 - "ProjectRelatedLink"
Cohesion: 0.19
Nodes (10): ModelViewSet, Meta, ProjectRelatedLinkBaseForm, ProjectRelatedLinkUpdateForm, The base form for creating and updating a…, The form we use to update an existing…, ProjectRelatedLink, A ``ProjectRelatedLink`` is a link to an external resource that is related to a… (+2 more)

### Community 20 - "SphinxHostingBreadcrumbs"
Cohesion: 0.11
Nodes (9): BreadcrumbBlock, Build breadcrumbs for the SearchNote detail page. Returns: Breadcrumb trail for…, Build breadcrumbs for the SearchNote create page. Returns: Breadcrumb trail for…, Build breadcrumbs for the SearchNote update page. Returns: Breadcrumb trail for…, Build breadcrumbs for the SearchNote list page. Returns: Breadcrumb trail for…, Return our breadcrumbs for this page:: Home -> Project -> Version ->…, Return our breadcrumbs for this page:: Home -> Project -> Version ->…, The breadcrumbs that appear at the top of each page. (+1 more)

### Community 21 - "Project"
Cohesion: 0.14
Nodes (5): SearchForm, GlobalSearchForm, The search form at the top of the sidebar, underneath the logo. It is a…, Project, A Project is what a set of Sphinx docs describes: an application, a library,…

### Community 22 - "demo/settings.py"
Cohesion: 0.13
Nodes (10): Command, Any, BaseCommand, Run demo migrations and seed baseline data when the database is fresh. If…, Determine whether the configured database has never run migrations. Args:…, Apply demo bootstrap tasks for the active environment. Args: *args: Positional…, censor_password_processor(), Automatically censors any logging context key called "password", "password1",… (+2 more)

### Community 23 - "SphinxHostingMainMenu"
Cohesion: 0.17
Nodes (11): AbstractUser, Menu, MenuItem, The primary menu that appears in :py:class:`SphinxHostingSidebar`. It appears…, Build deterministic static menu items for this request. Args: items: The base…, Build conditional items provided by ``django-sphinx-hosting`` itself. Args:…, Build conditional items from configured menu builder callables. Args: request:…, Mark the active item across all menu entries. Args: items: Menu items to mark… (+3 more)

### Community 24 - "ClassifierFilterBlock"
Cohesion: 0.20
Nodes (10): CrispyFormModalWidget, ClassifierFilterBlock, CardWidget, A :py:class:`wildewidgets.CardWidget` that contains the…, ProjectCreateModalWidget, ProjectRelatedLinkCreateModalWidget, ProjectRelatedLinkUpdateModalWidget, A modal dialog that holds the… (+2 more)

### Community 25 - "SearchNoteDetailView"
Cohesion: 0.09
Nodes (22): ListView, DeleteView, DetailView, HttpRequest, HttpResponse, LoginRequiredMixin, Return notes with related project and classifier data loaded. Returns: Queryset…, Build the widget layout for one SearchNote detail page. Returns: Populated… (+14 more)

### Community 26 - "SearchNoteIndex"
Cohesion: 0.20
Nodes (6): Return the indexed Django model. Returns: The ``SearchNote`` model class., Build the unified-search document for one note. Args: obj: The note being…, Prepare classifier facet values for one note. Args: obj: The note being…, Return the queryset used for bulk indexing. Keyword Args: using: The Haystack…, Haystack index for demo ``SearchNote`` objects., SearchNoteIndex

### Community 27 - "test_search_note_integration.py"
Cohesion: 0.46
Nodes (7): _make_note_fixture(), _make_user(), needs_demo, test_search_note_crud_flow(), test_search_note_list_and_detail_pages_render(), test_search_notes_fixture_is_loaded_by_migration(), test_seed_search_notes_command_creates_ten_notes()

### Community 28 - "test_unified_search_extensibility.py"
Cohesion: 0.06
Nodes (58): BaseGlobalSphinxPageSearchView, _build_view(), clear_search_renderer_state(), _create_search_note(), _create_search_page(), DummyForm, DummyUser, FakeSearchQuerySet (+50 more)

### Community 29 - "Project"
Cohesion: 0.16
Nodes (15): VersionUploadForm, Project, ProjectRelatedLink, Version, ProjectRelatedLinksWidget, VersionUploadBlock, API Read vs Write Access, Administrators (+7 more)

### Community 30 - "validators.py"
Cohesion: 0.25
Nodes (4): MachineNameField, A form field for our :py:class:`sphinx_hosting.fields.MachineNameField` that…, Migration, Migration

### Community 31 - "ProjectTable"
Cohesion: 0.14
Nodes (9): ActionButtonModelTable, ProjectTable, QuerySet, Displays a `dataTable <https://datatables.net>`_ of our…, Render our ``latest_version`` column. This is the version string of the…, Render our ``latest_version_date`` column. This is the last modified date of…, Render our ``classifiers`` column. Args: row: the ``Project`` we are rendering…, Filter our results by the ``value``, a comma separated list of… (+1 more)

### Community 32 - "test_host_project_can_extend_navigation_without_losing_defaults"
Cohesion: 0.50
Nodes (3): needs_demo, override_settings, test_host_project_can_extend_navigation_without_losing_defaults()

### Community 33 - ".get_content"
Cohesion: 0.14
Nodes (11): ListModelWidget, Widget, Build the project detail layout and apply host-project extensions. Returns: The…, ProjectClassifierListWidget, ProjectRelatedLinkListItemWidget, ProjectRelatedLinksListWidget, Block, HorizontalLayoutBlock (+3 more)

### Community 34 - "test_project_detail_customization_integration.py"
Cohesion: 0.67
Nodes (3): needs_demo, test_host_project_can_extend_project_detail_layout_without_losing_defaults(), test_host_project_can_extend_project_update_layout_without_losing_defaults()

### Community 35 - ".get_queryset"
Cohesion: 0.12
Nodes (11): ModelForm, Form, HttpRequest, HttpResponse, ModelSearchForm, QuerySet, If the form is invalid, we want to display the errors to the user and redirect…, If ``version`` is ``latest``, return the latest version of the… (+3 more)

### Community 36 - "ProjectRelatedLinksWidget"
Cohesion: 0.16
Nodes (9): RowModelUrlButton, LatestVersionButton, ProjectRelatedLinksWidget, ProjectTableWidget, AbstractUser, CardWidget, WidgetListLayoutHeader, A :py:class:`wildewidgets.CardWidget` that gives our :py:class:`ProjectTable`… (+1 more)

### Community 37 - "render_search_note_result"
Cohesion: 0.18
Nodes (11): AbstractUser, Block, GlobalSphinxPageSearchView, HttpRequest, SearchResult, Widget, Result card used to render a demo ``SearchNote`` search hit. Args: note: The…, Initialize this demo search-result card. Args: note: The note represented by… (+3 more)

### Community 41 - "SPHINX_HOSTING_SETTINGS"
Cohesion: 0.24
Nodes (11): EXCLUDE_FROM_LATEST, EXTRA_MENU_ITEMS, MENU_ITEM_BUILDERS, PROJECT_DETAIL_LAYOUT_BUILDERS, SPHINX_HOSTING_SETTINGS, Strict Navigation Item Configuration, EXTRA_MENU_ITEMS, MENU_ITEM_BUILDERS (+3 more)

### Community 42 - "navigation.py"
Cohesion: 0.25
Nodes (10): _get_app_setting(), get_menu_item_builders(), MenuItemBuilder, Any, Protocol, Resolve dotted import paths to callable builder objects. Args: paths: Dotted…, Return configured conditional menu-item builders. Returns: A tuple of resolved…, Protocol for a conditional menu-item builder callable. The callable may return… (+2 more)

### Community 43 - "django-sphinx-hosting"
Cohesion: 0.22
Nodes (10): Classifier, ClassifierManager, ClassifierNode, django-sphinx-hosting, Unified Search, Authenticated Docs Viewing, django-sphinx-hosting, Search Across All Projects (+2 more)

### Community 44 - "Global Table of Contents"
Cohesion: 0.22
Nodes (10): SphinxGlobalTOCHTMLProcessor, SphinxPage, SphinxPageGlobalTableOfContentsMenu, Global Table of Contents, Sphinx Heading Level Strategy, Next Previous Parent Navigation, JSON Page Tree Traversal, sphinxcontrib-jsonglobaltoc (+2 more)

### Community 45 - "seed_search_notes.py"
Cohesion: 0.20
Nodes (7): Command, Any, BaseCommand, Create or update the demo ``SearchNote`` records used by the sandbox app., Upsert the curated demo ``SearchNote`` records and related metadata. Args:…, Immutable seed definition for one demo ``SearchNote`` record. Args: title:…, SearchNoteSeed

### Community 46 - "SearchNoteCreateView"
Cohesion: 0.14
Nodes (14): Any, CreateView, UpdateView, Widget, Create a new demo ``SearchNote`` record., Inject the current form action URL into the model form. Returns: Keyword…, Build the widget layout for the SearchNote create page. Returns: Populated…, Update an existing demo ``SearchNote`` record. (+6 more)

### Community 47 - ".__init__"
Cohesion: 0.22
Nodes (6): ProjectVersionTable, BasicModelTable, Displays a `dataTable <https://datatables.net>`_ of our…, One of our ``kwargs`` must be ``project_id``, the ``pk`` of the…, Render our ``num_pages`` column. This is the number of…, Render our ``num_images`` column. This is the number of…

### Community 49 - "django-sphinx-hosting REST API"
Cohesion: 0.22
Nodes (9): sphinxcontrib-openapi, OpenAPI v1 Schema, Django REST Framework, TokenAuthentication, /api/v1/, django-sphinx-hosting REST API, API Token Authentication, /api/v1/version/import/ (+1 more)

### Community 51 - "extend_project_detail_layout"
Cohesion: 0.25
Nodes (9): ProjectDetailView, build_search_notes_menu_item(), extend_project_detail_layout(), AbstractUser, CardWidget, HttpRequest, WidgetListLayout, Return a demo note-browser link for conditional menu-builder integration.… (+1 more)

### Community 53 - "SphinxHostingSidebar"
Cohesion: 0.25
Nodes (8): django-wildewidgets, EXTRA_MENU_ITEMS, SphinxHostingSidebar, django-crispy-forms, django-theme-academy, django-wildewidgets, NAVBAR_CLASS, NAVBAR_CLASS

### Community 54 - "0003_load_search_notes_fixture.py"
Cohesion: 0.29
Nodes (7): load_fixture(), Migration, noop_reverse(), Any, Load the demo ``SearchNote`` fixture after the schema is in place. Args: apps:…, Leave demo fixture rows untouched when reversing this migration. Args: apps:…, Load the demo ``SearchNote`` fixture after the schema alignment migration.

### Community 56 - ".__init__"
Cohesion: 0.32
Nodes (5): Any, Form, QuerySet, Store the note displayed by the widget. Args: note: Note instance displayed on…, Store the form and labels used by the form widget. Args: form: Bound or unbound…

### Community 57 - ".save"
Cohesion: 0.25
Nodes (4): Overrides :py:meth:`django.db.models.Model.save`. Override save to create any…, Set the :py:attr:`SphinxPage.searchable` flag on the searchable pages in this…, Purge the cached output from our :py:meth:`globaltoc` property., Overriding :py:meth:`django.db.models.Model.save` here so that we can purge our…

### Community 58 - "GlobalSearchFormWidget"
Cohesion: 0.25
Nodes (7): CustomNavbar, The vertical menu area on the left of the page. It houses our search form,…, SphinxHostingSidebar, GlobalSearchFormWidget, CrispyFormWidget, Encapsulates the :py:class:`sphinx_hosting.forms.GlobalSearchForm`., TablerVerticalNavbar

### Community 59 - "SEARCH_RESULT_RENDERERS"
Cohesion: 0.29
Nodes (7): django-haystack, OpenSearch Haystack Backend, SEARCH_RESULT_RENDERERS, project_id and classifiers Facet Fields, Haystack SearchIndex, SEARCH_RESULT_RENDERERS, SearchNote Demo Model

### Community 60 - "_normalize_builder_result"
Cohesion: 0.38
Nodes (7): MenuItemSpec, _normalize_builder_result(), _normalize_menu_item(), _normalize_menu_items(), Normalize one menu item spec into a :py:class:`wildewidgets.MenuItem`. Args:…, Normalize a collection of menu item specs. Args: items: The menu item specs to…, Normalize a builder return value into menu items. Args: result: The raw builder…

### Community 62 - "Command"
Cohesion: 0.40
Nodes (4): Command, BaseCommand, **Usage**: ``./manage.py fix_broken_hrefs`` This is a one-shot command to fix…, Given an HTML body of a Sphinx page, update the ``<a href="path">`` references…

### Community 64 - "0010_add_groups.py"
Cohesion: 0.29
Nodes (6): apply_migration(), Migration, Create default ``django-sphinx-hosting`` auth groups and permissions., Create the default auth groups and assign their permissions. Args: apps: The…, Remove the auth groups created by :func:`apply_migration`. Args: apps: The…, revert_migration()

### Community 65 - ".__call__"
Cohesion: 0.33
Nodes (4): MenuBuilderResult, HttpRequest, Return the current request from ``django-crequest`` middleware. Returns: The…, Build conditional menu items for one request/user. Keyword Args: request: The…

### Community 66 - "wait-for-it.sh"
Cohesion: 0.73
Nodes (5): echoerr(), wait-for-it.sh script, usage(), wait_for(), wait_for_wrapper()

### Community 67 - "16x16 Favicon"
Cohesion: 0.40
Nodes (6): Blue Circular Badge, Browser Tab Icon, 16x16 Favicon, High-Contrast Lettermark, Sphinx Documentation Brand, Sphinx S Lettermark

### Community 69 - "0015_migrate_to_latest_version_field.py"
Cohesion: 0.33
Nodes (5): Migration, Set the :py:attr:`sphinx_hosting.models.Project.latest_version` field to None…, Set the :py:attr:`sphinx_hosting.models.Project.latest_version` field for all…, set_latest_version(), unset_latest_version()

### Community 70 - "sphinx_rtd_theme Required Theme"
Cohesion: 0.40
Nodes (5): sphinx_rtd_theme, SphinxPackageImporter, Sphinx JSON Tarball Package, html_theme_options collapse_navigation False, sphinx_rtd_theme Required Theme

### Community 71 - "Android Chrome 512x512 App Icon"
Cohesion: 0.50
Nodes (5): Solid Blue Circular Badge, Android Chrome 512x512 App Icon, PWA Android Chrome Touch Icon, White Serif Capital S, Sphinx Brand Mark

### Community 72 - "Apple Touch Icon"
Cohesion: 0.40
Nodes (5): Apple Touch Icon, Circular Badge Layout, iOS Home Screen Icon, Sphinx, Sphinx S Monogram

### Community 73 - "Favicon 32x32"
Cohesion: 0.50
Nodes (5): Browser Tab Identity, Blue Circular Badge, Favicon 32x32, Serif S Monogram, Sphinx Brand Initial

### Community 75 - "sphinxdocument_url"
Cohesion: 0.40
Nodes (5): simple_tag, Return the URL to the :py:class:`sphinx_hosting.models.SphinxImage` identified…, Return the URL to the :py:class:`sphinx_hosting.models.SphinxDocument`…, sphinxdocument_url(), sphinximage_url()

### Community 76 - "SphinxHostingAppConfig"
Cohesion: 0.40
Nodes (3): AppConfig, Runs as soon as the app is loaded. It loads our signal receivers., SphinxHostingAppConfig

### Community 77 - "Sphinx Hosting Logo"
Cohesion: 0.70
Nodes (5): Horizontal Icon-Wordmark Lockup, Sphinx Hosting Brand, Sphinx Hosting Logo, Sphinx Line-Art Icon, Sphinx Hosting Wordmark

### Community 78 - "PageTreeNode"
Cohesion: 0.50
Nodes (4): PageTreeNode, SphinxPageTree, SphinxPageTreeProcessor, TreeNode

### Community 79 - "Demo Users admin editor viewer"
Cohesion: 0.50
Nodes (4): Project Managers, Version Managers, Viewers, Demo Users admin editor viewer

### Community 80 - "Android Chrome 192x192 Icon"
Cohesion: 0.67
Nodes (4): Android Chrome 192x192 Icon, Circular Lettermark Logo, Android Chrome PWA Homescreen Icon, Sphinx Lettermark S

### Community 84 - "SphinxHostingApiAppConfig"
Cohesion: 0.50
Nodes (3): AppConfig, The app config for the sphinx_hosting.api app., SphinxHostingApiAppConfig

### Community 86 - "sandbox/demo Django Project"
Cohesion: 0.67
Nodes (3): sandbox/demo Django Project, Testing Contract, sandbox Demo Application

### Community 87 - "California Institute of Technology"
Cohesion: 0.67
Nodes (3): California Institute of Technology, Caltech IMSS Academic Development Services, MIT License

## Ambiguous Edges - Review These
- `White Serif Capital S` → `Sphinx Brand Mark`  [AMBIGUOUS]
  sandbox/demo/core/static/core/images/android-chrome-512x512.png · relation: conceptually_related_to

## Knowledge Gaps
- **128 isolated node(s):** `release.sh script`, `django-sphinx-hosting`, `collectstatic.sh script`, `entrypoint.sh script`, `restart_gunicorn.sh script` (+123 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **54 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `White Serif Capital S` and `Sphinx Brand Mark`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `Version` connect `Version` to `SphinxPackageImporter`, `.__init__`, `.get_queryset`, `ProjectReadonlyUpdateForm`, `test_navigation_extensibility.py`, `sphinx_hosting/views.py`, `Classifier`, `.__init__`, `test_unified_search_integration.py`, `SphinxGlobalTOCHTMLProcessor`, `ProjectRelatedLink`, `Project`, `.save`, `test_unified_search_extensibility.py`, `ProjectTable`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Why does `SphinxPackageImporter` connect `SphinxPackageImporter` to `.get_queryset`, `ProjectReadonlyUpdateForm`, `sphinx_hosting/views.py`, `Classifier`, `Version`, `ProjectRelatedLink`, `Project`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Why does `Project` connect `Project` to `SphinxPackageImporter`, `test_project_detail_extensibility.py`, `ProjectReadonlyUpdateForm`, `wildewidgets/search.py`, `SearchNote`, `sphinx_hosting/views.py`, `Classifier`, `Version`, `.get_content`, `test_unified_search_integration.py`, `ProjectRelatedLink`, `ClassifierFilterBlock`, `test_search_note_integration.py`, `test_unified_search_extensibility.py`, `ProjectTable`, `.get_content`, `test_project_detail_customization_integration.py`, `ProjectRelatedLinksWidget`, `seed_search_notes.py`, `extend_project_detail_layout`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Are the 36 inferred relationships involving `Project` (e.g. with `GlobalSearchForm` and `Meta`) actually correct?**
  _`Project` has 36 INFERRED edges - model-reasoned connections that need verification._
- **Are the 32 inferred relationships involving `Version` (e.g. with `GlobalSearchForm` and `Meta`) actually correct?**
  _`Version` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 39 inferred relationships involving `SphinxPackageImporter` (e.g. with `ClassifierFilter` and `ClassifierViewSet`) actually correct?**
  _`SphinxPackageImporter` has 39 INFERRED edges - model-reasoned connections that need verification._