# ruff: noqa: S101, S106, PLR2004

import pytest
from django.test import override_settings

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@override_settings(
    SPHINX_HOSTING_SETTINGS={
        "NAVBAR_CLASS": "demo.core.wildewidgets.MainMenu",
        "MENU_ITEM_BUILDERS": ["demo.core.wildewidgets.build_search_notes_menu_item"],
    }
)
def test_host_project_can_extend_navigation_without_losing_defaults(
    client, django_user_model
):
    user = django_user_model.objects.create_user(
        username="menu-user",
        password="secret",
        is_staff=True,
    )
    client.force_login(user)
    response = client.get("/")
    assert response.status_code == 200
    html = response.content.decode()
    assert "Projects" in html
    assert "Search Notes" in html
