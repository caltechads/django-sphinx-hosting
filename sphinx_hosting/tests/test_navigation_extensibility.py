# ruff: noqa: S101, SLF001

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest
from crequest.middleware import CrequestMiddleware
from django.test import override_settings
from wildewidgets import Menu, MenuItem

from sphinx_hosting.views import (
    ClassifierViewSet,
    ProjectListView,
    get_configured_navbar_class,
)
from sphinx_hosting.wildewidgets import SphinxHostingMainMenu, SphinxHostingSidebar

BUILDER_CALLS: list[tuple[Any, Any, Any]] = []


class CustomNavbar(SphinxHostingSidebar):
    pass


class NotANavbar:
    pass


def builder_support(*, request, user, menu):
    BUILDER_CALLS.append((request, user, menu))
    return {"text": "Support", "icon": "life-preserver", "url": "/support/"}


def builder_admin(*, request, user, menu):
    del request, user, menu
    return [MenuItem(text="Admin", icon="shield", url="/admin/")]


def builder_invalid(*, request, user, menu):
    del request, user, menu
    return "bad builder result"


def builder_raises(*, request, user, menu):
    del request, user, menu
    msg = "builder exploded"
    raise RuntimeError(msg)


@dataclass
class DummyUser:
    can_view_classifier: bool

    def has_perm(self, permission: str) -> bool:
        return permission == "sphinxhostingcore.view_classifier" and (
            self.can_view_classifier
        )


@dataclass
class DummyRequest:
    user: DummyUser


def _capture_built_items(monkeypatch):
    captured: dict[str, list[MenuItem]] = {}

    def fake_build_menu(self, items):
        del self
        captured["items"] = list(items)

    monkeypatch.setattr(Menu, "build_menu", fake_build_menu)
    return captured


def _build_menu(
    monkeypatch,
    *,
    can_view_classifier: bool = False,
    active_item: str | None = None,
) -> list[MenuItem]:
    captured = _capture_built_items(monkeypatch)
    request = DummyRequest(user=DummyUser(can_view_classifier=can_view_classifier))
    monkeypatch.setattr(
        CrequestMiddleware, "get_request", staticmethod(lambda: request)
    )
    menu = SphinxHostingMainMenu()
    if active_item:
        menu.activate(active_item)
    menu.build_menu(menu._items)
    return captured["items"]


@override_settings(
    SPHINX_HOSTING_SETTINGS={
        "EXTRA_MENU_ITEMS": [{"text": "Static Docs", "icon": "book", "url": "/docs/"}],
        "MENU_ITEM_BUILDERS": [
            "sphinx_hosting.tests.test_navigation_extensibility.builder_support",
            "sphinx_hosting.tests.test_navigation_extensibility.builder_admin",
        ],
    }
)
def test_menu_build_order_and_activation(monkeypatch):
    BUILDER_CALLS.clear()
    items = _build_menu(
        monkeypatch, can_view_classifier=True, active_item="Support"
    )
    assert [item.text for item in items] == [
        "Projects",
        "Static Docs",
        "Classifiers",
        "Support",
        "Admin",
    ]
    assert BUILDER_CALLS
    assert BUILDER_CALLS[0][2].__class__ is SphinxHostingMainMenu
    assert any(item.text == "Support" and item.active for item in items)


@override_settings(
    SPHINX_HOSTING_SETTINGS={
        "EXTRA_MENU_ITEMS": [{"text": "Static Docs", "unknown": "value"}]
    }
)
def test_extra_menu_items_reject_unknown_keys(monkeypatch):
    with pytest.raises(ValueError, match="unknown keys"):
        _build_menu(monkeypatch)


@override_settings(
    SPHINX_HOSTING_SETTINGS={
        "MENU_ITEM_BUILDERS": [
            "sphinx_hosting.tests.test_navigation_extensibility.builder_invalid"
        ]
    }
)
def test_menu_builder_rejects_invalid_return_type(monkeypatch):
    with pytest.raises(TypeError, match="must return None"):
        _build_menu(monkeypatch)


@override_settings(
    SPHINX_HOSTING_SETTINGS={
        "MENU_ITEM_BUILDERS": [
            "sphinx_hosting.tests.test_navigation_extensibility.builder_raises"
        ]
    }
)
def test_menu_builder_exception_propagates(monkeypatch):
    with pytest.raises(RuntimeError, match="builder exploded"):
        _build_menu(monkeypatch)


@override_settings(SPHINX_HOSTING_SETTINGS={})
def test_classifiers_menu_item_uses_permission(monkeypatch):
    denied_items = _build_menu(monkeypatch, can_view_classifier=False)
    allowed_items = _build_menu(monkeypatch, can_view_classifier=True)
    assert "Classifiers" not in [item.text for item in denied_items]
    assert "Classifiers" in [item.text for item in allowed_items]


@override_settings(SPHINX_HOSTING_SETTINGS={})
def test_navbar_class_defaults_to_sphinx_hosting_sidebar():
    assert get_configured_navbar_class() is SphinxHostingSidebar


@override_settings(
    SPHINX_HOSTING_SETTINGS={
        "NAVBAR_CLASS": (
            "sphinx_hosting.tests.test_navigation_extensibility.CustomNavbar"
        )
    }
)
def test_navbar_class_setting_resolves():
    assert get_configured_navbar_class() is CustomNavbar


@override_settings(SPHINX_HOSTING_SETTINGS={"NAVBAR_CLASS": 3})
def test_navbar_class_setting_requires_dotted_path_string():
    with pytest.raises(TypeError, match="dotted-path string"):
        get_configured_navbar_class()


@override_settings(
    SPHINX_HOSTING_SETTINGS={
        "NAVBAR_CLASS": "sphinx_hosting.tests.test_navigation_extensibility.NotANavbar"
    }
)
def test_navbar_class_setting_requires_navbar_subclass():
    with pytest.raises(TypeError, match="Navbar subclass"):
        get_configured_navbar_class()


@override_settings(
    SPHINX_HOSTING_SETTINGS={
        "NAVBAR_CLASS": (
            "sphinx_hosting.tests.test_navigation_extensibility.CustomNavbar"
        )
    }
)
def test_viewset_and_menu_mixin_use_shared_navbar_resolver():
    viewset = ClassifierViewSet(url_prefix="lookups", url_namespace="sphinx_hosting")
    assert viewset.navbar_class is CustomNavbar

    view = ProjectListView()
    assert view.get_navbar_class() is CustomNavbar
