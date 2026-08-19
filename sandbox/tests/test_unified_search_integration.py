# ruff: noqa: S101, S106, PLR2004

from __future__ import annotations

import pytest
from demo.core.models import SearchNote
from haystack import connections

from sphinx_hosting.models import Classifier, Project, SphinxPage, Version

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture(autouse=True)
def clear_search_backend():
    backend = connections["default"].get_backend()
    backend.clear(models=[SphinxPage, SearchNote])
    yield
    backend.clear(models=[SphinxPage, SearchNote])


def _refresh_search_backend() -> None:
    """
    Refresh the active Haystack backend when the backend exposes a refresh API.

    Side Effects:
        Flushes pending search index writes for OpenSearch-backed tests.

    """
    backend = connections["default"].get_backend()
    if hasattr(backend, "conn") and hasattr(backend, "index_name"):
        backend.conn.indices.refresh(index=backend.index_name)


def _index_instance(instance) -> None:
    """
    Index one model instance into the active Haystack backend.

    Args:
        instance: The Django model instance to index.

    Side Effects:
        Updates the search index for the instance model.

    """
    index = connections["default"].get_unified_index().get_index(instance.__class__)
    index.update_object(instance, using="default")
    _refresh_search_backend()


def _create_search_fixture(
    *,
    search_term: str,
    classifier_name: str = "docs",
) -> tuple[SphinxPage, SearchNote, Classifier]:
    suffix = Project.objects.count() + 1
    classifier, _ = Classifier.objects.get_or_create(name=classifier_name)
    project = Project.objects.create(
        title="Unified Search Project",
        machine_name=f"unified-search-project-{suffix}",
    )
    project.classifiers.add(classifier)
    version = Version.objects.create(project=project, version="1.0.0")
    page = SphinxPage.objects.create(
        version=version,
        relative_path="index",
        content="{}",
        title=f"Built-in Alpha Page {suffix}",
        orig_body=f"<p>{search_term} built-in page body</p>",
        body=f"<p>{search_term} built-in page body</p>",
        searchable=True,
    )
    version.head = page
    version.save()
    project.latest_version = version
    project.save()
    note = SearchNote.objects.create(
        title=f"Host Alpha Note {suffix}",
        body=f"{search_term} host note body",
        project=project,
    )
    note.classifiers.add(classifier)
    _index_instance(page)
    _index_instance(note)
    return page, note, classifier


def test_unified_search_renders_built_in_and_host_hits_together(
    client, django_user_model
):
    user = django_user_model.objects.create_user(
        username="unified-search-user",
        password="secret",
        is_staff=True,
    )
    page, note, _ = _create_search_fixture(search_term="alpha-signal")

    client.force_login(user)
    response = client.get("/search/?q=alpha-signal")

    assert response.status_code == 200
    html = response.content.decode()
    assert page.title in html
    assert note.title in html
    assert "Demo Search Note" in html
    assert "Host Project Results" not in html


def test_unified_search_project_facet_filters_built_in_and_host_hits(
    client, django_user_model
):
    user = django_user_model.objects.create_user(
        username="unified-search-project-user",
        password="secret",
        is_staff=True,
    )
    matching_page, matching_note, _ = _create_search_fixture(
        search_term="project-shared"
    )
    other_page, other_note, _ = _create_search_fixture(search_term="project-shared")

    client.force_login(user)
    response = client.get(
        f"/search/?q=project-shared&project_id={matching_note.project_id}"
    )

    assert response.status_code == 200
    html = response.content.decode()
    assert matching_page.title in html
    assert matching_note.title in html
    assert other_page.title not in html
    assert other_note.title not in html


def test_unified_search_classifier_facet_filters_built_in_and_host_hits(
    client, django_user_model
):
    user = django_user_model.objects.create_user(
        username="unified-search-classifier-user",
        password="secret",
        is_staff=True,
    )
    matching_page, matching_note, matching_classifier = _create_search_fixture(
        search_term="classifier-shared",
        classifier_name="matched-docs",
    )
    other_page, other_note, _ = _create_search_fixture(
        search_term="classifier-shared",
        classifier_name="other-docs",
    )

    client.force_login(user)
    response = client.get(
        f"/search/?q=classifier-shared&classifiers={matching_classifier.name}"
    )

    assert response.status_code == 200
    html = response.content.decode()
    assert matching_page.title in html
    assert matching_note.title in html
    assert other_page.title not in html
    assert other_note.title not in html


def test_unified_search_omits_hits_for_non_matching_queries(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="unified-search-empty-user",
        password="secret",
        is_staff=True,
    )
    _create_search_fixture(search_term="gamma-signal")

    client.force_login(user)
    response = client.get("/search/?q=no-match-token")

    assert response.status_code == 200
    html = response.content.decode()
    assert "Built-in Alpha Page" not in html
    assert "Host Alpha Note" not in html
