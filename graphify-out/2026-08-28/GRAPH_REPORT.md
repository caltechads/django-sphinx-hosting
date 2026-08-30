# Graph Report - django-sphinx-hosting  (2026-08-28)

## Corpus Check
- 145 files · ~77,340 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1521 nodes · 3027 edges · 169 communities (114 shown, 55 thin omitted)
- Extraction: 78% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 650 edges (avg confidence: 0.56)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6864424f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- SphinxPackageImporter
- .__init__
- check_napoleon_gate.py
- Version
- test_project_detail_extensibility.py
- sphinx_hosting/views.py
- test_navigation_extensibility.py
- sphinx_page.py
- .__init__
- SearchNote
- SphinxPageIndex
- Classifier
- AGENTS.md
- ClassifierNode
- APIUser
- Product Contract
- .get_content
- test_unified_search_integration.py
- SphinxGlobalTOCHTMLProcessor
- .run
- SphinxHostingBreadcrumbs
- test_version_make_latest.py
- demo/settings.py
- SphinxHostingMainMenu
- project.py
- Version
- NoHTMLValidator
- test_search_note_integration.py
- get_search_result_renderers
- Project
- sphinx_hosting/models.py
- ProjectTable
- test_host_project_can_extend_navigation_without_losing_defaults
- .get_content
- test_project_detail_customization_integration.py
- HttpResponse
- ProjectRelatedLinksWidget
- render_search_note_result
- TreeNode
- SphinxPage
- importers.py
- SPHINX_HOSTING_SETTINGS
- navigation.py
- django-sphinx-hosting
- Global Table of Contents
- seed_search_notes.py
- SearchNoteDetailView
- .__init__
- ClassifierFilterForm
- django-sphinx-hosting REST API
- Make Latest is authorized by change_project or change_version, scoped to the URL Project
- extend_project_detail_layout
- wildewidgets/search.py
- SphinxHostingSidebar
- 0003_load_search_notes_fixture.py
- Sphinx Hosting
- GlobalSphinxPageSearchView
- test_unified_search_extensibility.py
- GlobalSearchFormWidget
- SEARCH_RESULT_RENDERERS
- _normalize_builder_result
- Project
- Command
- SearchNoteIndex
- 0010_add_groups.py
- .__call__
- wait-for-it.sh
- 16x16 Favicon
- project_detail_layout.py
- 0015_migrate_to_latest_version_field.py
- sphinx_rtd_theme Required Theme
- Android Chrome 512x512 App Icon
- Apple Touch Icon
- Favicon 32x32
- Host-side mermaid Implementation Plan
- SphinxPageTree
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
- .import_pages
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
- Command
- playwright
- SearchNoteCreateView
- build_search_result_widget
- sphinxdocument_url
- .__init__
- Host-side mermaid.js renders `.mermaid` in the Page Body

## God Nodes (most connected - your core abstractions)
1. `Project` - 94 edges
2. `Version` - 79 edges
3. `SphinxPackageImporter` - 63 edges
4. `SphinxPage` - 61 edges
5. `SearchNote` - 43 edges
6. `ProjectRelatedLink` - 43 edges
7. `Classifier` - 41 edges
8. `VersionMakeLatestForm` - 31 edges
9. `ProjectReadonlyUpdateForm` - 30 edges
10. `VersionUploadForm` - 29 edges

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

## Communities (169 total, 55 thin omitted)

### Community 0 - "SphinxPackageImporter"
Cohesion: 0.14
Nodes (44): action, Response, AddVersionPermission, ChangeProjectPermission, APIView, Request, Check to see if the user can add versions. Note: This is really only useful on…, Check to see if the user can change projects. Note: This is only for use in on… (+36 more)

### Community 1 - ".__init__"
Cohesion: 0.06
Nodes (27): Generate the set of widgets for this page. Returns: A populated page layout, BasicModelTable, CardWidget, WidgetListLayoutHeader, A :py:class:`wildewidgets.CardWidget` that gives our…, Displays a `dataTable <https://datatables.net>`_ of our…, Gives a :py:class:`wildewidget.Datagrid` type overview of information about…, One of our ``kwargs`` must be ``version_id``, the ``pk`` of the… (+19 more)

### Community 2 - "check_napoleon_gate.py"
Cohesion: 0.07
Nodes (45): AsyncFunctionDef, _check_file(), _check_function_doc(), _constructor_has_args(), _first_doc_line(), _function_has_args(), _function_has_keyword_args(), _function_uses_return_or_yield() (+37 more)

### Community 3 - "Version"
Cohesion: 0.06
Nodes (42): django-haystack, django-theme-academy, django-wildewidgets, Django REST Framework, drf-spectacular, elasticsearch, mysqlclient, sphinxcontrib-openapi (+34 more)

### Community 4 - "test_project_detail_extensibility.py"
Cohesion: 0.14
Nodes (21): BaseProjectUpdateView, build_project_detail_layout(), build_project_update_layout(), clear_builder_state(), DummyUser, django_db, fixture, override_settings (+13 more)

### Community 5 - "sphinx_hosting/views.py"
Cohesion: 0.11
Nodes (36): BaseProjectDetailView, MessageMixin, ModelViewSet, NavbarMixin, SearchView, ProjectReadonlyUpdateForm, ProjectRelatedLinkUpdateForm, ProjectUpdateForm (+28 more)

### Community 6 - "test_navigation_extensibility.py"
Cohesion: 0.08
Nodes (32): Navbar, _build_menu(), builder_admin(), _capture_built_items(), DummyRequest, DummyUser, NotANavbar, MenuItem (+24 more)

### Community 7 - "sphinx_page.py"
Cohesion: 0.10
Nodes (24): test_body_widget_preserves_mustaches_in_mermaid(), test_empty_and_plain_html_unchanged(), test_leaves_image_tags_outside_mermaid(), test_skips_highlight_mermaid_and_language_mermaid(), test_wraps_div_and_extra_classes(), test_wraps_pre_mermaid_and_template_keeps_mustaches(), Render-time helpers for mermaid blocks in a Page Body., Wrap mermaid elements in ``{% verbatim %}`` so Django ``Template`` does not… (+16 more)

### Community 8 - ".__init__"
Cohesion: 0.17
Nodes (14): Header, PagedSearchLayout, PagedSearchResultsBlock, Block, HorizontalLayoutBlock, PagedModelWidget, SearchQuerySet, SearchResult (+6 more)

### Community 9 - "SearchNote"
Cohesion: 0.11
Nodes (15): Meta, Form used to create and update demo ``SearchNote`` records. Keyword Args:…, Configure crispy layout and sorted relation choices for the form. Args: *args:…, SearchNoteForm, Meta, TimeStampedModel, Demo-only searchable content used to exercise unified global search.…, Return the visible label for this note. Returns: The note title. (+7 more)

### Community 10 - "SphinxPageIndex"
Cohesion: 0.12
Nodes (13): Make the version the latest version., Model, QuerySet, Search index for SphinxPage model., Return the SphinxPage model class., Used when the entire index for model is updated. Keyword Args: using: The alias…, Remove all pages for a version from the index. Args: version: The version whose…, Reindex all pages for a project. This happens when we get a new latest_version… (+5 more)

### Community 11 - "Classifier"
Cohesion: 0.07
Nodes (32): BaseCreateView, BaseFormView, BaseUpdateView, FormInvalidMessageMixin, FormValidMessageMixin, MultiplePermissionsRequiredMixin, PermissionRequiredMixin, ProjectCreateForm (+24 more)

### Community 12 - "AGENTS.md"
Cohesion: 0.17
Nodes (11): AGENTS.md, Architecture (Required), AWS Interaction, Documentation Contract (Required), graphify, Implementation Priority (Required), Post-Implementation Quality Gate (Required), Project Structure (Mandatory) (+3 more)

### Community 13 - "ClassifierNode"
Cohesion: 0.24
Nodes (7): Command, BaseCommand, Tree, **Usage**: ``./manage.py print_classifier_tree`` Print the…, Parse the tree of :py:class:`sphinx_hosting.models.ClassifierNode` objects we…, TreePrinter, ClassifierNode

### Community 14 - "APIUser"
Cohesion: 0.10
Nodes (15): Command, BaseCommand, Command, BaseCommand, Migration, APIUser, APIUserManager, finalize_api_user() (+7 more)

### Community 15 - "Product Contract"
Cohesion: 0.08
Nodes (25): Acceptance Examples, Actors, Assumptions, Definition of Done, Goal Capsule, Implementation Units, Key Decisions, Key Flows (+17 more)

### Community 16 - ".get_content"
Cohesion: 0.18
Nodes (10): Widget, Build the project update layout and apply host-project extensions. Returns: The…, Widget, ProjectClassifierSelectorWidget, ProjectInfoWidget, ProjectVersionsTableWidget, A :py:class:`wildewidgets.CardWidget` containing a Tabler datagrid that gives…, A :py:class:`wildewidgets.CardWidget` that gives our… (+2 more)

### Community 17 - "test_unified_search_integration.py"
Cohesion: 0.26
Nodes (11): clear_search_backend(), _create_search_fixture(), _index_instance(), fixture, Refresh the active Haystack backend when the backend exposes a refresh API.…, Index one model instance into the active Haystack backend. Args: instance: The…, _refresh_search_backend(), test_unified_search_classifier_facet_filters_built_in_and_host_hits() (+3 more)

### Community 18 - "SphinxGlobalTOCHTMLProcessor"
Cohesion: 0.15
Nodes (12): HtmlElement, Any, Build a :py:class:`wildewdigets.MenuItem` compatible dict representing…, Build a :py:class:`wildewdigets.MenuItem` compatible dict representing…, Parse the :py:func:`Version.page_tree` and return a struct that works with…, **Usage**: ``SphinxGlobalTOCHTMLProcessor().run(version, globaltoc_html)```…, Process ``html``, an ``lxml`` parsed set of elements representing the contents…, Parse our global table of contents HTML blob and return a list of… (+4 more)

### Community 19 - ".run"
Cohesion: 0.14
Nodes (10): BufferedReader, IO, Look through the member names in our tarfile ``package`` for ``filename``, and…, Load the ``globalcontext.json`` file for later reference. Args: package: the…, Look in ``package`` for a member named ``globalcontext.json``, and load that…, Import all downloadable documents in our Sphinx documentation into the database…, Import all images in our Sphinx documentation into the database before…, Given :py:attr:`page_tree``, a list of page linkages (parent, next, prev), link… (+2 more)

### Community 20 - "SphinxHostingBreadcrumbs"
Cohesion: 0.11
Nodes (9): BreadcrumbBlock, Build breadcrumbs for the SearchNote detail page. Returns: Breadcrumb trail for…, Build breadcrumbs for the SearchNote create page. Returns: Breadcrumb trail for…, Build breadcrumbs for the SearchNote update page. Returns: Breadcrumb trail for…, Build breadcrumbs for the SearchNote list page. Returns: Breadcrumb trail for…, Return our breadcrumbs for this page:: Home -> Project -> Version ->…, Return our breadcrumbs for this page:: Home -> Project -> Version ->…, The breadcrumbs that appear at the top of each page. (+1 more)

### Community 21 - "test_version_make_latest.py"
Cohesion: 0.22
Nodes (22): parametrize, alpha_project(), beta_project(), _create_version_with_head(), _grant_permissions(), _login_with_permissions(), _make_latest_url(), django_db (+14 more)

### Community 22 - "demo/settings.py"
Cohesion: 0.13
Nodes (10): Command, Any, BaseCommand, Run demo migrations and seed baseline data when the database is fresh. If…, Determine whether the configured database has never run migrations. Args:…, Apply demo bootstrap tasks for the active environment. Args: *args: Positional…, censor_password_processor(), Automatically censors any logging context key called "password", "password1",… (+2 more)

### Community 23 - "SphinxHostingMainMenu"
Cohesion: 0.17
Nodes (11): AbstractUser, Menu, MenuItem, The primary menu that appears in :py:class:`SphinxHostingSidebar`. It appears…, Build deterministic static menu items for this request. Args: items: The base…, Build conditional items provided by ``django-sphinx-hosting`` itself. Args:…, Build conditional items from configured menu builder callables. Args: request:…, Mark the active item across all menu entries. Args: items: Menu items to mark… (+3 more)

### Community 24 - "project.py"
Cohesion: 0.14
Nodes (15): CrispyFormModalWidget, RowModelUrlButton, ClassifierFilterBlock, CardWidget, A :py:class:`wildewidgets.CardWidget` that contains the…, LatestVersionButton, ProjectCreateModalWidget, ProjectRelatedLinkCreateModalWidget (+7 more)

### Community 25 - "Version"
Cohesion: 0.12
Nodes (13): Overrides :py:meth:`django.db.models.Model.save`. Override save to create any…, A ``Version`` is a specific version of a :py:class:`Project`. Versions own…, Set the :py:attr:`SphinxPage.searchable` flag on the searchable pages in this…, Purge the cached output from our :py:meth:`globaltoc` property., Overriding :py:meth:`django.db.models.Model.save` here so that we can purge our…, Version, QuerySet, Handles displaying the details page for a… (+5 more)

### Community 26 - "NoHTMLValidator"
Cohesion: 0.18
Nodes (7): deconstructible, ClassifierManager, Manager for :py:class:`Classifier` models., Given our classifiers, which are ``::`` separated lists of terms like:: Section…, NoHTMLValidator, Raises a ValidationError if the given value contains any HTML., Add a unique hash for the validator.

### Community 27 - "test_search_note_integration.py"
Cohesion: 0.46
Nodes (7): _make_note_fixture(), _make_user(), needs_demo, test_search_note_crud_flow(), test_search_note_list_and_detail_pages_render(), test_search_notes_fixture_is_loaded_by_migration(), test_seed_search_notes_command_creates_ten_notes()

### Community 28 - "get_search_result_renderers"
Cohesion: 0.26
Nodes (11): test_search_result_renderers_default_to_empty(), get_search_result_models(), get_search_result_renderers(), Model, Protocol, Return configured host-model search result renderers. Returns: A mapping of…, Return host-model classes included in unified global search. Returns: A tuple…, Protocol for a unified-search result renderer callable. Each renderer converts… (+3 more)

### Community 29 - "Project"
Cohesion: 0.16
Nodes (15): VersionUploadForm, Project, ProjectRelatedLink, Version, ProjectRelatedLinksWidget, VersionUploadBlock, API Read vs Write Access, Administrators (+7 more)

### Community 30 - "sphinx_hosting/models.py"
Cohesion: 0.12
Nodes (16): MachineNameField, A :py:class:`django.forms.SlugField` that also allows "." characters. "." is…, MachineNameField, A form field for our :py:class:`sphinx_hosting.fields.MachineNameField` that…, Migration, Migration, Migration, Migration (+8 more)

### Community 31 - "ProjectTable"
Cohesion: 0.14
Nodes (9): ActionButtonModelTable, ProjectTable, QuerySet, Displays a `dataTable <https://datatables.net>`_ of our…, Render our ``latest_version`` column. This is the version string of the…, Render our ``latest_version_date`` column. This is the last modified date of…, Render our ``classifiers`` column. Args: row: the ``Project`` we are rendering…, Filter our results by the ``value``, a comma separated list of… (+1 more)

### Community 32 - "test_host_project_can_extend_navigation_without_losing_defaults"
Cohesion: 0.50
Nodes (3): needs_demo, override_settings, test_host_project_can_extend_navigation_without_losing_defaults()

### Community 33 - ".get_content"
Cohesion: 0.14
Nodes (12): ListModelWidget, Widget, Build the project detail layout and apply host-project extensions. Returns: The…, ProjectClassifierListWidget, ProjectDetailWidget, ProjectRelatedLinksListWidget, Block, CrispyFormWidget (+4 more)

### Community 34 - "test_project_detail_customization_integration.py"
Cohesion: 0.67
Nodes (3): needs_demo, test_host_project_can_extend_project_detail_layout_without_losing_defaults(), test_host_project_can_extend_project_update_layout_without_losing_defaults()

### Community 35 - "HttpResponse"
Cohesion: 0.18
Nodes (8): ModelForm, Form, HttpRequest, HttpResponse, ModelSearchForm, If the form is invalid, we want to display the errors to the user and redirect…, Persist the Make Latest change. Side Effects: Writes ``Project.latest_version``…, Flash form errors and redirect to the project detail page. Args: form: The form…

### Community 36 - "ProjectRelatedLinksWidget"
Cohesion: 0.21
Nodes (7): ProjectRelatedLinksWidget, ProjectTableWidget, AbstractUser, CardWidget, WidgetListLayoutHeader, A :py:class:`wildewidgets.CardWidget` that gives our :py:class:`ProjectTable`…, A :py:class:`wildewidgets.CardWidget` that allows us to manage the…

### Community 37 - "render_search_note_result"
Cohesion: 0.18
Nodes (11): AbstractUser, Block, GlobalSphinxPageSearchView, HttpRequest, SearchResult, Widget, Result card used to render a demo ``SearchNote`` search hit. Args: note: The…, Initialize this demo search-result card. Args: note: The note represented by… (+3 more)

### Community 38 - "TreeNode"
Cohesion: 0.18
Nodes (9): Command, ArgumentParser, BaseCommand, Tree, Parse the tree of :py:class:`sphinx_hosting.models.TreeNode` objects we get…, **Usage**: ``./manage.py print_doctree <project_machine_name> <version…, TreePrinter, A :py:class:`dataclass` that we use with :py:class:`SphinxPageTree` to build… (+1 more)

### Community 39 - "SphinxPage"
Cohesion: 0.19
Nodes (8): A ``SphinxPage`` is a single page of a set of Sphinx documentation.…, Return the permalink for this page. This is the URL for the page with the…, SphinxPage, Prepare the classifiers for the SphinxPage. Args: obj: The SphinxPage object…, QuerySet, Filter our :py:class:`sphinx_hosting.models.SphinxPage` objects by…, Filter our :py:class:`sphinx_hosting.models.SphinxPage` objects by…, Filter our :py:class:`sphinx_hosting.models.SphinxPage` objects by…

### Community 40 - "importers.py"
Cohesion: 0.22
Nodes (8): Exception, VersionAlreadyExists, PageTreeNode, A data structure to temporarily hold relationships between…, Command, ArgumentParser, BaseCommand, Import a Sphinx documentation tarfile into the database. We will use the the…

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

### Community 46 - "SearchNoteDetailView"
Cohesion: 0.09
Nodes (22): ListView, DeleteView, DetailView, HttpRequest, HttpResponse, LoginRequiredMixin, Return notes with related project and classifier data loaded. Returns: Queryset…, Build the widget layout for one SearchNote detail page. Returns: Populated… (+14 more)

### Community 47 - ".__init__"
Cohesion: 0.22
Nodes (6): ProjectVersionTable, BasicModelTable, Displays a `dataTable <https://datatables.net>`_ of our…, One of our ``kwargs`` must be ``project_id``, the ``pk`` of the…, Render our ``num_pages`` column. This is the number of…, Render our ``num_images`` column. This is the number of…

### Community 48 - "ClassifierFilterForm"
Cohesion: 0.29
Nodes (7): ClassifierFilterForm, Block, HorizontalLayoutBlock, Add a subtree of classifier checkboxes. Args: contents: the ``<ul>`` block to…, Build and return the :py:class:`wildewidgets.CheckboxInputBlock` for the…, The tree-like classifier filter form that appears to the right of the…, UnorderedList

### Community 49 - "django-sphinx-hosting REST API"
Cohesion: 0.22
Nodes (9): sphinxcontrib-openapi, OpenAPI v1 Schema, Django REST Framework, TokenAuthentication, /api/v1/, django-sphinx-hosting REST API, API Token Authentication, /api/v1/version/import/ (+1 more)

### Community 50 - "Make Latest is authorized by change_project or change_version, scoped to the URL Project"
Cohesion: 0.40
Nodes (4): Consequences, Considered Options, Make Latest is authorized by change_project or change_version, scoped to the URL Project, Status

### Community 51 - "extend_project_detail_layout"
Cohesion: 0.25
Nodes (9): ProjectDetailView, build_search_notes_menu_item(), extend_project_detail_layout(), AbstractUser, CardWidget, HttpRequest, WidgetListLayout, Return a demo note-browser link for conditional menu-builder integration.… (+1 more)

### Community 52 - "wildewidgets/search.py"
Cohesion: 0.11
Nodes (26): Row, FacetBlock, Base class for blocks that appear to the right of the search results listing on…, A :py:class:`FacetBlock` that allows the user to filter search results by…, A :py:class:`FacetBlock` that allows the user to filter search results by…, The header for the entire search results page. This shows the search string…, SearchResultsClassifiersFacet, SearchResultsPageHeader (+18 more)

### Community 53 - "SphinxHostingSidebar"
Cohesion: 0.25
Nodes (8): django-wildewidgets, EXTRA_MENU_ITEMS, SphinxHostingSidebar, django-crispy-forms, django-theme-academy, django-wildewidgets, NAVBAR_CLASS, NAVBAR_CLASS

### Community 54 - "0003_load_search_notes_fixture.py"
Cohesion: 0.29
Nodes (7): load_fixture(), Migration, noop_reverse(), Any, Load the demo ``SearchNote`` fixture after the schema is in place. Args: apps:…, Leave demo fixture rows untouched when reversing this migration. Args: apps:…, Load the demo ``SearchNote`` fixture after the schema alignment migration.

### Community 56 - "GlobalSphinxPageSearchView"
Cohesion: 0.14
Nodes (13): BaseGlobalSphinxPageSearchView, _apply_global_search_facets(), GlobalSphinxPageSearchView, HttpRequest, HttpResponse, ModelSearchForm, SearchQuerySet, Widget (+5 more)

### Community 57 - "test_unified_search_extensibility.py"
Cohesion: 0.11
Nodes (26): _build_view(), clear_search_renderer_state(), _create_search_note(), _create_search_page(), DummyForm, DummyUser, FakeSearchQuerySet, _make_result() (+18 more)

### Community 58 - "GlobalSearchFormWidget"
Cohesion: 0.25
Nodes (7): CustomNavbar, The vertical menu area on the left of the page. It houses our search form,…, SphinxHostingSidebar, GlobalSearchFormWidget, CrispyFormWidget, Encapsulates the :py:class:`sphinx_hosting.forms.GlobalSearchForm`., TablerVerticalNavbar

### Community 59 - "SEARCH_RESULT_RENDERERS"
Cohesion: 0.29
Nodes (7): django-haystack, OpenSearch Haystack Backend, SEARCH_RESULT_RENDERERS, project_id and classifiers Facet Fields, Haystack SearchIndex, SEARCH_RESULT_RENDERERS, SearchNote Demo Model

### Community 60 - "_normalize_builder_result"
Cohesion: 0.38
Nodes (7): MenuItemSpec, _normalize_builder_result(), _normalize_menu_item(), _normalize_menu_items(), Normalize one menu item spec into a :py:class:`wildewidgets.MenuItem`. Args:…, Normalize a collection of menu item specs. Args: items: The menu item specs to…, Normalize a builder return value into menu items. Args: result: The raw builder…

### Community 61 - "Project"
Cohesion: 0.11
Nodes (10): SearchForm, GlobalSearchForm, Meta, ProjectRelatedLinkBaseForm, ProjectRelatedLinkCreateForm, The base form for creating and updating a…, The search form at the top of the sidebar, underneath the logo. It is a…, The form we use to create a new… (+2 more)

### Community 62 - "Command"
Cohesion: 0.33
Nodes (4): Command, BaseCommand, **Usage**: ``./manage.py fix_broken_hrefs`` This is a one-shot command to fix…, Given an HTML body of a Sphinx page, update the ``<a href="path">`` references…

### Community 63 - "SearchNoteIndex"
Cohesion: 0.20
Nodes (6): Return the indexed Django model. Returns: The ``SearchNote`` model class., Build the unified-search document for one note. Args: obj: The note being…, Prepare classifier facet values for one note. Args: obj: The note being…, Return the queryset used for bulk indexing. Keyword Args: using: The Haystack…, Haystack index for demo ``SearchNote`` objects., SearchNoteIndex

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

### Community 68 - "project_detail_layout.py"
Cohesion: 0.20
Nodes (13): apply_project_detail_layout_builders(), ProjectDetailLayoutBuilder, ProjectDetailLayoutView, AbstractUser, HttpRequest, Protocol, WidgetListLayout, Apply configured project-detail layout builders to ``layout``. Keyword Args:… (+5 more)

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

### Community 74 - "Host-side mermaid Implementation Plan"
Cohesion: 0.22
Nodes (8): File structure, Global Constraints, Host-side mermaid Implementation Plan, Out of scope (do not do), Self-review, Task 1: `wrap_mermaid_verbatim`, Task 2: Wire `SphinxPageBodyWidget`, Task 3: Vendor mermaid, load it, overflow CSS

### Community 75 - "SphinxPageTree"
Cohesion: 0.21
Nodes (5): Return a list of the pages represented in this tree., Build a :py:class:`TreeNode` from ``page``. Note: This does not populate…, Return the page hierarchy for the set of :py:class:`SphinxPage` pages in this…, A class that holds the page hierarchy for the set of :py:class:`SphinxPage`…, SphinxPageTree

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

### Community 91 - ".import_pages"
Cohesion: 0.28
Nodes (5): Any, Ensure that there is a ``title`` key in ``data``, the JSON data from our .fjson…, Update our page's local table of contents (``data['toc']`) to have the CSS…, Update :py:attr:`page_tree`, our page linkage tree, with ``page``, which we…, Import a all pages from ``package`` into the database as…

### Community 146 - "Command"
Cohesion: 0.29
Nodes (4): Command, ArgumentParser, BaseCommand, **Usage**: ``./manage.py print_globaltoc <project_machine_name> <version…

### Community 164 - "SearchNoteCreateView"
Cohesion: 0.14
Nodes (14): Any, CreateView, UpdateView, Widget, Create a new demo ``SearchNote`` record., Inject the current form action URL into the model form. Returns: Keyword…, Build the widget layout for the SearchNote create page. Returns: Populated…, Update an existing demo ``SearchNote`` record. (+6 more)

### Community 165 - "build_search_result_widget"
Cohesion: 0.33
Nodes (8): build_search_result_widget(), AbstractUser, GlobalSphinxPageSearchView, HttpRequest, SearchResult, Widget, Build the widget used to render one unified-search result. Keyword Args:…, Render a unified-search hit. Keyword Args: result: The Haystack search hit to…

### Community 166 - "sphinxdocument_url"
Cohesion: 0.40
Nodes (5): simple_tag, Return the URL to the :py:class:`sphinx_hosting.models.SphinxImage` identified…, Return the URL to the :py:class:`sphinx_hosting.models.SphinxDocument`…, sphinxdocument_url(), sphinximage_url()

### Community 167 - ".__init__"
Cohesion: 0.32
Nodes (5): Any, Form, QuerySet, Store the note displayed by the widget. Args: note: Note instance displayed on…, Store the form and labels used by the form widget. Args: form: Bound or unbound…

### Community 168 - "Host-side mermaid.js renders `.mermaid` in the Page Body"
Cohesion: 0.40
Nodes (4): Consequences, Considered Options, Host-side mermaid.js renders `.mermaid` in the Page Body, Status

## Ambiguous Edges - Review These
- `White Serif Capital S` → `Sphinx Brand Mark`  [AMBIGUOUS]
  sandbox/demo/core/static/core/images/android-chrome-512x512.png · relation: conceptually_related_to

## Knowledge Gaps
- **162 isolated node(s):** `release.sh script`, `django-sphinx-hosting`, `collectstatic.sh script`, `entrypoint.sh script`, `restart_gunicorn.sh script` (+157 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **55 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `White Serif Capital S` and `Sphinx Brand Mark`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `Project` connect `Project` to `SphinxPackageImporter`, `test_project_detail_extensibility.py`, `sphinx_hosting/views.py`, `SearchNote`, `SphinxPageIndex`, `Classifier`, `.get_content`, `test_unified_search_integration.py`, `test_version_make_latest.py`, `project.py`, `Version`, `NoHTMLValidator`, `test_search_note_integration.py`, `sphinx_hosting/models.py`, `ProjectTable`, `.get_content`, `test_project_detail_customization_integration.py`, `importers.py`, `seed_search_notes.py`, `extend_project_detail_layout`, `wildewidgets/search.py`, `test_unified_search_extensibility.py`, `project_detail_layout.py`?**
  _High betweenness centrality (0.090) - this node is a cross-community bridge._
- **Why does `SphinxPage` connect `SphinxPage` to `SphinxPackageImporter`, `sphinx_hosting/views.py`, `sphinx_page.py`, `SphinxPageIndex`, `Classifier`, `test_unified_search_integration.py`, `SphinxGlobalTOCHTMLProcessor`, `test_version_make_latest.py`, `Version`, `NoHTMLValidator`, `get_search_result_renderers`, `sphinx_hosting/models.py`, `TreeNode`, `importers.py`, `wildewidgets/search.py`, `GlobalSphinxPageSearchView`, `test_unified_search_extensibility.py`, `Command`, `.import_pages`?**
  _High betweenness centrality (0.063) - this node is a cross-community bridge._
- **Why does `Version` connect `Version` to `SphinxPackageImporter`, `.__init__`, `sphinx_hosting/views.py`, `test_navigation_extensibility.py`, `sphinx_page.py`, `SphinxPageIndex`, `Classifier`, `test_unified_search_integration.py`, `Command`, `.run`, `SphinxGlobalTOCHTMLProcessor`, `test_version_make_latest.py`, `project.py`, `NoHTMLValidator`, `sphinx_hosting/models.py`, `ProjectTable`, `TreeNode`, `importers.py`, `.__init__`, `test_unified_search_extensibility.py`, `Project`, `SphinxPageTree`, `.import_pages`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Are the 36 inferred relationships involving `Project` (e.g. with `GlobalSearchForm` and `Meta`) actually correct?**
  _`Project` has 36 INFERRED edges - model-reasoned connections that need verification._
- **Are the 32 inferred relationships involving `Version` (e.g. with `GlobalSearchForm` and `Meta`) actually correct?**
  _`Version` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 39 inferred relationships involving `SphinxPackageImporter` (e.g. with `ClassifierFilter` and `ClassifierViewSet`) actually correct?**
  _`SphinxPackageImporter` has 39 INFERRED edges - model-reasoned connections that need verification._