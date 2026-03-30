# ruff: noqa: S101, S106, PLR2004

from __future__ import annotations

import pytest
from django.core.management import call_command

from demo.core.models import SearchNote
from demo.core.search_note_seed import SEARCH_NOTE_SEED_COUNT
from sphinx_hosting.models import Classifier, Project

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def _make_user(django_user_model, *, username: str):
    return django_user_model.objects.create_user(
        username=username,
        password="secret",
        is_staff=True,
    )


def _make_note_fixture() -> tuple[SearchNote, Project, Classifier]:
    project = Project.objects.create(
        title="Search Note Project",
        machine_name="search-note-project",
    )
    classifier = Classifier.objects.create(name="search-note-fixture")
    project.classifiers.add(classifier)
    note = SearchNote.objects.create(
        title="Unified Search Checklist",
        body="Search notes make host-model results easy to demo.",
        project=project,
    )
    note.classifiers.add(classifier)
    return note, project, classifier


def test_search_note_list_and_detail_pages_render(client, django_user_model):
    user = _make_user(django_user_model, username="search-note-reader")
    note, _, classifier = _make_note_fixture()

    client.force_login(user)
    list_response = client.get("/notes/")
    detail_response = client.get(note.get_absolute_url())

    assert list_response.status_code == 200
    assert detail_response.status_code == 200
    assert note.title in list_response.content.decode()
    assert note.title in detail_response.content.decode()
    assert classifier.name in detail_response.content.decode()


def test_search_note_crud_flow(client, django_user_model):
    user = _make_user(django_user_model, username="search-note-editor")
    project = Project.objects.create(
        title="CRUD Project",
        machine_name="crud-project",
    )
    alpha = Classifier.objects.create(name="alpha")
    beta = Classifier.objects.create(name="beta")
    project.classifiers.add(alpha, beta)

    client.force_login(user)

    create_response = client.post(
        "/notes/create/",
        {
            "title": "Navigation recipe",
            "project": project.pk,
            "classifiers": [alpha.pk],
            "body": "Use menu builders when note links depend on the request.",
        },
    )

    assert create_response.status_code == 302
    note = SearchNote.objects.get(title="Navigation recipe")
    assert list(note.classifiers.values_list("name", flat=True)) == ["alpha"]

    update_response = client.post(
        note.get_update_url(),
        {
            "title": "Navigation recipe updated",
            "project": project.pk,
            "classifiers": [alpha.pk, beta.pk],
            "body": (
                "Use menu builders for conditional links and extra menu items "
                "for static links."
            ),
        },
    )

    assert update_response.status_code == 302
    note.refresh_from_db()
    assert note.title == "Navigation recipe updated"
    assert set(note.classifiers.values_list("name", flat=True)) == {"alpha", "beta"}

    delete_response = client.post(note.get_delete_url())

    assert delete_response.status_code == 302
    assert SearchNote.objects.filter(pk=note.pk).count() == 0


def test_seed_search_notes_command_creates_ten_notes():
    call_command("seed_search_notes")

    assert SearchNote.objects.count() == SEARCH_NOTE_SEED_COUNT
    assert Project.objects.filter(machine_name="demo-extension-recipes").exists()
    assert Classifier.objects.filter(name="search").exists()
    assert SearchNote.objects.filter(classifiers__name="authorization").count() >= 1

    call_command("seed_search_notes")

    assert SearchNote.objects.count() == SEARCH_NOTE_SEED_COUNT


def test_search_notes_fixture_is_loaded_by_migration():
    assert SearchNote.objects.count() == SEARCH_NOTE_SEED_COUNT
    assert Project.objects.filter(machine_name="demo-search-recipes").exists()
    assert Classifier.objects.filter(name="packaging").exists()
    assert (
        SearchNote.objects.filter(
            title__icontains="Unified search works when host models"
        ).count()
        == 1
    )
