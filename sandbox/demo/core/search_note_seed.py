from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class SearchNoteSeed:
    """
    Immutable seed definition for one demo ``SearchNote`` record.

    Args:
        title: Human-readable title shown in the CRUD UI and unified search.
        body: Concise note body adapted from repository documentation.
        project_title: Display title for the related demo ``Project``.
        project_machine_name: Machine name for the related demo ``Project``.
        classifiers: Classifier names associated with the note and project.
        source_paths: Repository documentation paths that informed the note text.

    """

    #: Human-readable title shown in the CRUD UI and unified search.
    title: str
    #: Concise note body adapted from repository documentation.
    body: str
    #: Display title for the related demo ``Project``.
    project_title: str
    #: Machine name for the related demo ``Project``.
    project_machine_name: str
    #: Classifier names associated with the note and project.
    classifiers: tuple[str, ...]
    #: Repository documentation paths that informed the note text.
    source_paths: tuple[str, ...]


#: Demo notes adapted from the repository overview documentation.
SEARCH_NOTE_SEEDS: Final[tuple[SearchNoteSeed, ...]] = (
    SearchNoteSeed(
        title="Administrators and editors cover different permission tiers",
        body=(
            "Administrators can manage projects, versions, and classifiers. "
            "Editors can still create and update projects and versions, but "
            "they do not manage classifier records."
        ),
        project_title="Demo Operations Guide",
        project_machine_name="demo-operations-guide",
        classifiers=("authorization", "operations"),
        source_paths=("doc/source/overview/authorization.rst",),
    ),
    SearchNoteSeed(
        title="Viewers can search and read without changing content",
        body=(
            "Users who are not assigned to the higher-privilege groups remain "
            "viewers. They can browse documentation and use search, but they "
            "cannot create, modify, or delete hosted records."
        ),
        project_title="Demo Operations Guide",
        project_machine_name="demo-operations-guide",
        classifiers=("authorization", "search"),
        source_paths=("doc/source/overview/authorization.rst",),
    ),
    SearchNoteSeed(
        title="API clients usually start with token authentication",
        body=(
            "The REST API commonly uses DRF token authentication. The demo docs "
            "call out the required parser and filter backends, then show how to "
            "send the token in the Authorization header."
        ),
        project_title="Demo API Recipes",
        project_machine_name="demo-api-recipes",
        classifiers=("api", "authorization"),
        source_paths=("doc/source/overview/api.rst",),
    ),
    SearchNoteSeed(
        title="Imported docs should ship as a tarball containing a json/ folder",
        body=(
            "Packaging works best when the tarball keeps every generated JSON "
            "asset under a top-level json/ directory. That bundle shape lets the "
            "importer find searchindex.json, object metadata, and static assets."
        ),
        project_title="Demo Import Pipeline",
        project_machine_name="demo-import-pipeline",
        classifiers=("importing", "packaging"),
        source_paths=(
            "doc/source/overview/importing.rst",
            "doc/source/overview/packaging.rst",
        ),
    ),
    SearchNoteSeed(
        title="Docs can be imported from the UI, API, or a management command",
        body=(
            "The demo documentation describes three practical import paths: the "
            "project detail upload form, the version import API endpoint, and "
            "the import_docs management command for scripted workflows."
        ),
        project_title="Demo Import Pipeline",
        project_machine_name="demo-import-pipeline",
        classifiers=("importing", "api"),
        source_paths=("doc/source/overview/importing.rst",),
    ),
    SearchNoteSeed(
        title="Project names must line up with the Sphinx conf.py project value",
        body=(
            "A hosted Project should use the same machine name that the Sphinx "
            "conf.py file exposes as project. Matching those names keeps imports "
            "predictable and lets new versions land on the expected record."
        ),
        project_title="Demo Packaging Guide",
        project_machine_name="demo-packaging-guide",
        classifiers=("packaging",),
        source_paths=("doc/source/overview/packaging.rst",),
    ),
    SearchNoteSeed(
        title="Authoring quality depends on disciplined heading and toctree structure",
        body=(
            "Root pages should keep a top-level heading and hide their toctree, "
            "while child pages use consistent heading levels. Clean heading "
            "discipline produces better next/previous links and sidebar nesting."
        ),
        project_title="Demo Authoring Handbook",
        project_machine_name="demo-authoring-handbook",
        classifiers=("authoring", "navigation"),
        source_paths=("doc/source/overview/authoring.rst",),
    ),
    SearchNoteSeed(
        title=(
            "Static and conditional menu hooks support host-project "
            "navigation tweaks"
        ),
        body=(
            "Always-on links belong in EXTRA_MENU_ITEMS, while request-aware "
            "links belong in MENU_ITEM_BUILDERS. That split lets a host project "
            "add simple permanent links or compute items at request time."
        ),
        project_title="Demo Extension Recipes",
        project_machine_name="demo-extension-recipes",
        classifiers=("navigation", "customization"),
        source_paths=("doc/source/overview/navigation_customization.rst",),
    ),
    SearchNoteSeed(
        title="Project detail builders can append widgets and sidebar actions",
        body=(
            "PROJECT_DETAIL_LAYOUT_BUILDERS receive the live layout object for "
            "a project page. Host code can append widgets, add sidebar links, "
            "and wire small action buttons without replacing the package view."
        ),
        project_title="Demo Extension Recipes",
        project_machine_name="demo-extension-recipes",
        classifiers=("customization", "navigation"),
        source_paths=("doc/source/overview/project_detail_customization.rst",),
    ),
    SearchNoteSeed(
        title="Unified search works when host models expose matching facet fields",
        body=(
            "A host model joins unified search by supplying a Haystack "
            "SearchIndex and a SEARCH_RESULT_RENDERERS entry. Matching the "
            "project_id and classifiers facet fields keeps host results aligned "
            "with the built-in project and classifier filters."
        ),
        project_title="Demo Search Recipes",
        project_machine_name="demo-search-recipes",
        classifiers=("search", "customization"),
        source_paths=("doc/source/overview/unified_search.rst",),
    ),
)

#: The number of notes created by the demo seed command.
SEARCH_NOTE_SEED_COUNT: Final[int] = len(SEARCH_NOTE_SEEDS)
