# ruff: noqa: S101, S106

from __future__ import annotations

from http import HTTPStatus
from unittest.mock import patch
from uuid import uuid4

import pytest
from django.contrib.auth.models import Permission
from django.contrib.messages import get_messages
from django.urls import reverse

from sphinx_hosting.forms import VersionMakeLatestForm
from sphinx_hosting.models import Project, Version


@pytest.fixture
def alpha_project() -> Project:
    return Project.objects.create(title="Alpha Project", machine_name="alpha")


@pytest.fixture
def beta_project() -> Project:
    return Project.objects.create(title="Beta Project", machine_name="beta")


@pytest.mark.django_db
def test_clean_version_accepts_version_in_url_project(alpha_project: Project) -> None:
    version = Version.objects.create(project=alpha_project, version="1.0.0")

    form = VersionMakeLatestForm(
        data={"version": version.pk},
        project_machine_name="alpha",
    )

    assert form.is_valid()
    assert form.cleaned_data["version"] == version.pk


@pytest.mark.django_db
def test_clean_version_rejects_unknown_pk() -> None:
    with patch.object(VersionMakeLatestForm, "save") as save_mock:
        form = VersionMakeLatestForm(
            data={"version": 999_999},
            project_machine_name="alpha",
        )

        assert not form.is_valid()
        assert "version" in form.errors
        save_mock.assert_not_called()


@pytest.mark.django_db
def test_clean_version_rejects_version_from_other_project(
    beta_project: Project,
) -> None:
    beta_version = Version.objects.create(project=beta_project, version="1.0.0")
    beta_project.latest_version = beta_version
    beta_project.save()

    with patch.object(VersionMakeLatestForm, "save") as save_mock:
        form = VersionMakeLatestForm(
            data={"version": beta_version.pk},
            project_machine_name="alpha",
        )

        assert not form.is_valid()
        assert "version" in form.errors
        save_mock.assert_not_called()

    beta_project.refresh_from_db()
    assert beta_project.latest_version_id == beta_version.pk


def _make_latest_url(slug: str) -> str:
    return reverse("sphinx_hosting:project--set-latest", kwargs={"slug": slug})


def _upload_url(slug: str) -> str:
    return reverse("sphinx_hosting:version--upload", kwargs={"slug": slug})


def _grant_permissions(user, *codenames: str) -> None:
    for codename in codenames:
        permission = Permission.objects.get(
            content_type__app_label="sphinxhostingcore",
            codename=codename,
        )
        user.user_permissions.add(permission)


def _login_with_permissions(client, django_user_model, username: str, *codenames: str):
    user = django_user_model.objects.create_user(
        username=f"{username}-{uuid4().hex[:8]}",
        password="secret",
    )
    _grant_permissions(user, *codenames)
    user = django_user_model.objects.get(pk=user.pk)
    client.force_login(user)
    return user


@pytest.mark.django_db
def test_anonymous_post_does_not_write_and_redirects_to_login(
    client, alpha_project: Project
) -> None:
    version = Version.objects.create(project=alpha_project, version="1.0.0")
    alpha_project.latest_version = version
    alpha_project.save()

    sibling = client.post(_upload_url("alpha"), data={"file": ""})
    response = client.post(_make_latest_url("alpha"), data={"version": version.pk})

    alpha_project.refresh_from_db()
    assert alpha_project.latest_version_id == version.pk
    assert response.status_code == sibling.status_code
    assert sibling.url.startswith("/accounts/login/")
    assert response.url.startswith("/accounts/login/")


@pytest.mark.django_db
def test_viewer_post_does_not_write_and_matches_sibling_denied(
    client, django_user_model, alpha_project: Project
) -> None:
    version = Version.objects.create(project=alpha_project, version="1.0.0")
    alpha_project.latest_version = version
    alpha_project.save()
    _login_with_permissions(client, django_user_model, "viewer")

    sibling = client.post(_upload_url("alpha"), data={"file": ""})
    response = client.post(_make_latest_url("alpha"), data={"version": version.pk})

    alpha_project.refresh_from_db()
    assert alpha_project.latest_version_id == version.pk
    assert response.status_code == sibling.status_code


@pytest.mark.django_db
def test_change_project_only_can_make_latest_for_own_version(
    client, django_user_model, alpha_project: Project
) -> None:
    old_latest = Version.objects.create(project=alpha_project, version="1.0.0")
    new_latest = Version.objects.create(project=alpha_project, version="2.0.0")
    alpha_project.latest_version = old_latest
    alpha_project.save()
    _login_with_permissions(client, django_user_model, "project-mgr", "change_project")

    with patch("sphinx_hosting.forms.SphinxPageIndex") as index_mock:
        response = client.post(
            _make_latest_url("alpha"), data={"version": new_latest.pk}
        )

    alpha_project.refresh_from_db()
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse(
        "sphinx_hosting:project--update", kwargs={"slug": "alpha"}
    )
    assert alpha_project.latest_version_id == new_latest.pk
    index_mock.return_value.remove_version.assert_called()
    index_mock.return_value.reindex_project.assert_called()


@pytest.mark.django_db
def test_change_version_only_can_make_latest_for_own_version(
    client, django_user_model, alpha_project: Project
) -> None:
    old_latest = Version.objects.create(project=alpha_project, version="1.0.0")
    new_latest = Version.objects.create(project=alpha_project, version="2.0.0")
    alpha_project.latest_version = old_latest
    alpha_project.save()
    _login_with_permissions(client, django_user_model, "version-mgr", "change_version")

    with patch("sphinx_hosting.forms.SphinxPageIndex") as index_mock:
        response = client.post(
            _make_latest_url("alpha"), data={"version": new_latest.pk}
        )

    alpha_project.refresh_from_db()
    assert response.status_code == HTTPStatus.FOUND
    assert alpha_project.latest_version_id == new_latest.pk
    index_mock.return_value.reindex_project.assert_called()


@pytest.mark.django_db
def test_foreign_version_pk_does_not_write_and_redirects_with_errors(
    client,
    django_user_model,
    alpha_project: Project,
    beta_project: Project,
) -> None:
    alpha_version = Version.objects.create(project=alpha_project, version="1.0.0")
    beta_version = Version.objects.create(project=beta_project, version="1.0.0")
    alpha_project.latest_version = alpha_version
    alpha_project.save()
    beta_project.latest_version = beta_version
    beta_project.save()
    _login_with_permissions(
        client, django_user_model, "project-mgr-ae4", "change_project"
    )

    response = client.post(
        _make_latest_url("alpha"), data={"version": beta_version.pk}
    )

    alpha_project.refresh_from_db()
    beta_project.refresh_from_db()
    assert alpha_project.latest_version_id == alpha_version.pk
    assert beta_project.latest_version_id == beta_version.pk
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse(
        "sphinx_hosting:project--update", kwargs={"slug": "alpha"}
    )
    flashed = " ".join(str(message) for message in get_messages(response.wsgi_request))
    assert "version" in flashed.lower()
    assert "does not belong to this project" in flashed
