# ruff: noqa: S101

from __future__ import annotations

from unittest.mock import patch

import pytest

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
