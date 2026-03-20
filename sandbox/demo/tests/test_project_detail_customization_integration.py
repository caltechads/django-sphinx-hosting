# ruff: noqa: S101, S106, PLR2004

import pytest
from django.contrib.auth.models import Permission

from sphinx_hosting.models import Project

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def test_host_project_can_extend_project_detail_layout_without_losing_defaults(
    client, django_user_model
):
    user = django_user_model.objects.create_user(
        username="project-layout-user",
        password="secret",
        is_staff=True,
    )
    project = Project.objects.create(
        title="Widget Project",
        machine_name="widget-project",
    )

    client.force_login(user)
    response = client.get(project.get_absolute_url())

    assert response.status_code == 200
    html = response.content.decode()
    assert "Project Info" in html
    assert "Host Ecosystem" in html
    assert "Project Support" in html


def test_host_project_can_extend_project_update_layout_without_losing_defaults(
    client, django_user_model
):
    user = django_user_model.objects.create_user(
        username="project-layout-editor",
        password="secret",
        is_staff=True,
    )
    user.user_permissions.add(Permission.objects.get(codename="change_project"))
    project = Project.objects.create(
        title="Widget Project",
        machine_name="widget-project-edit",
    )

    client.force_login(user)
    response = client.get(project.get_update_url())

    assert response.status_code == 200
    html = response.content.decode()
    assert "General Settings" in html
    assert "Host Ecosystem" in html
    assert "Project Support" in html
