# ruff: noqa: S101, SLF001

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, cast

import pytest
from django.test import RequestFactory, override_settings
from wildewidgets import Block, FormButton, LinkButton, WidgetListLayout

from sphinx_hosting.models import Project
from sphinx_hosting.project_detail_layout import (
    _resolve_project_detail_layout_builders,
    get_project_detail_layout_builders,
)
from sphinx_hosting.project_detail_view import ProjectDetailView
from sphinx_hosting.project_update_view import ProjectUpdateView
from sphinx_hosting.wildewidgets import (
    ProjectClassifierListWidget,
    ProjectClassifierSelectorWidget,
    ProjectDetailWidget,
    ProjectInfoWidget,
    ProjectRelatedLinkCreateModalWidget,
    ProjectRelatedLinksListWidget,
    ProjectRelatedLinksWidget,
    ProjectVersionsTableWidget,
)

LAYOUT_CALLS: list[tuple[Any, Any, Any, Any, Any]] = []
BUILDER_ORDER: list[str] = []
INVALID_LAYOUT_BUILDER = 3


@dataclass
class DummyUser:
    permissions: set[str] = field(default_factory=set)

    def has_perm(self, permission: str) -> bool:
        return permission in self.permissions


def builder_append_layout_content(*, request, user, project, layout, view):
    LAYOUT_CALLS.append((request, user, project, layout, view))
    widget = Block("Builder block body")
    widget.title = "Builder Block"
    layout.add_widget(widget)
    layout.add_sidebar_link_button("Builder Sidebar", "/builder/sidebar/")
    layout.add_sidebar_form_button("Builder Form", "/builder/form/")


def builder_first(*, request, user, project, layout, view):
    del request, user, project, view
    BUILDER_ORDER.append("first")
    widget = Block("First builder body")
    widget.title = "First Builder"
    layout.add_widget(widget)


def builder_second(*, request, user, project, layout, view):
    del request, user, project, view
    BUILDER_ORDER.append("second")
    widget = Block("Second builder body")
    widget.title = "Second Builder"
    layout.add_widget(widget)


def builder_raises(*, request, user, project, layout, view):
    del request, user, project, layout, view
    msg = "layout builder exploded"
    raise RuntimeError(msg)


@pytest.fixture(autouse=True)
def clear_builder_state():
    _resolve_project_detail_layout_builders.cache_clear()
    LAYOUT_CALLS.clear()
    BUILDER_ORDER.clear()
    yield
    _resolve_project_detail_layout_builders.cache_clear()
    LAYOUT_CALLS.clear()
    BUILDER_ORDER.clear()


def build_project_detail_layout(*, user: DummyUser | None = None) -> WidgetListLayout:
    request = RequestFactory().get("/projects/widget-project/")
    request.user = cast("Any", user if user is not None else DummyUser())
    project = Project.objects.create(
        title="Widget Project",
        machine_name=f"widget-project-{Project.objects.count() + 1}",
    )
    view = ProjectDetailView()
    view.request = request
    view.object = project
    layout = view.get_content()
    assert isinstance(layout, WidgetListLayout)
    return layout


def build_project_update_layout(*, user: DummyUser | None = None) -> WidgetListLayout:
    request = RequestFactory().get("/projects/widget-project/update/")
    request.user = cast("Any", user if user is not None else DummyUser())
    ProjectClassifierSelectorWidget.url_namespace = "sphinx_hosting"
    project = Project.objects.create(
        title="Widget Project",
        machine_name=f"widget-project-{Project.objects.count() + 1}",
    )
    view = ProjectUpdateView()
    view.request = request
    view.object = project
    layout = view.get_content()
    assert isinstance(layout, WidgetListLayout)
    return layout


@pytest.mark.django_db
@override_settings(
    SPHINX_HOSTING_SETTINGS={
        "PROJECT_DETAIL_LAYOUT_BUILDERS": [
            f"{__name__}.builder_append_layout_content"
        ]
    }
)
def test_project_detail_layout_builder_can_append_widgets_and_sidebar_actions():
    layout = build_project_detail_layout()

    assert LAYOUT_CALLS
    assert LAYOUT_CALLS[0][2].title == "Widget Project"
    assert isinstance(LAYOUT_CALLS[0][3], WidgetListLayout)
    assert isinstance(LAYOUT_CALLS[0][4], ProjectDetailView)

    entries = layout.main._entries
    assert [entry.__class__ for entry in entries[:5]] == [
        ProjectInfoWidget,
        ProjectDetailWidget,
        ProjectRelatedLinksListWidget,
        ProjectClassifierListWidget,
        ProjectVersionsTableWidget,
    ]
    assert entries[-1].title.header_text == "Builder Block"

    action_widgets = [wrapper.blocks[0] for wrapper in layout.sidebar._actions._widgets]
    assert any(isinstance(widget, LinkButton) for widget in action_widgets)
    assert any(isinstance(widget, FormButton) for widget in action_widgets)


@pytest.mark.django_db
@override_settings(
    SPHINX_HOSTING_SETTINGS={
        "PROJECT_DETAIL_LAYOUT_BUILDERS": [
            f"{__name__}.builder_append_layout_content"
        ]
    }
)
def test_project_update_layout_builder_preserves_defaults_and_uses_modals():
    layout = build_project_update_layout()

    assert LAYOUT_CALLS
    assert LAYOUT_CALLS[0][2].title == "Widget Project"
    assert isinstance(LAYOUT_CALLS[0][3], WidgetListLayout)
    assert isinstance(LAYOUT_CALLS[0][4], ProjectUpdateView)

    entries = layout.main._entries
    assert [entry.__class__ for entry in entries[:5]] == [
        ProjectInfoWidget,
        ProjectDetailWidget,
        ProjectRelatedLinksWidget,
        ProjectClassifierSelectorWidget,
        ProjectVersionsTableWidget,
    ]
    assert entries[-1].title.header_text == "Builder Block"

    assert len(layout.modals) == 1
    assert isinstance(layout.modals[0], ProjectRelatedLinkCreateModalWidget)
    assert not any(
        isinstance(entry, ProjectRelatedLinkCreateModalWidget) for entry in entries
    )

    action_widgets = [wrapper.blocks[0] for wrapper in layout.sidebar._actions._widgets]
    assert any(isinstance(widget, LinkButton) for widget in action_widgets)
    assert any(isinstance(widget, FormButton) for widget in action_widgets)


@pytest.mark.django_db
@override_settings(
    SPHINX_HOSTING_SETTINGS={
        "PROJECT_DETAIL_LAYOUT_BUILDERS": [
            f"{__name__}.builder_first",
            f"{__name__}.builder_second",
        ]
    }
)
def test_project_detail_layout_builders_run_in_configured_order():
    layout = build_project_detail_layout()

    assert BUILDER_ORDER == ["first", "second"]
    assert [entry.title.header_text for entry in layout.main._entries[-2:]] == [
        "First Builder",
        "Second Builder",
    ]


@override_settings(SPHINX_HOSTING_SETTINGS={})
def test_project_detail_layout_builders_default_to_empty():
    assert get_project_detail_layout_builders() == ()


@override_settings(SPHINX_HOSTING_SETTINGS={"PROJECT_DETAIL_LAYOUT_BUILDERS": 3})
def test_project_detail_layout_builders_requires_list():
    with pytest.raises(TypeError, match="must be a list of dotted-path strings"):
        get_project_detail_layout_builders()


@override_settings(
    SPHINX_HOSTING_SETTINGS={"PROJECT_DETAIL_LAYOUT_BUILDERS": [3]}
)
def test_project_detail_layout_builders_requires_string_entries():
    with pytest.raises(TypeError, match="must be a dotted-path string"):
        get_project_detail_layout_builders()


@override_settings(
    SPHINX_HOSTING_SETTINGS={
        "PROJECT_DETAIL_LAYOUT_BUILDERS": [
            f"{__name__}.INVALID_LAYOUT_BUILDER"
        ]
    }
)
def test_project_detail_layout_builders_requires_callable_targets():
    with pytest.raises(TypeError, match="which is not callable"):
        get_project_detail_layout_builders()


@pytest.mark.django_db
@override_settings(
    SPHINX_HOSTING_SETTINGS={
        "PROJECT_DETAIL_LAYOUT_BUILDERS": [
            f"{__name__}.builder_raises"
        ]
    }
)
def test_project_detail_layout_builder_exception_propagates():
    with pytest.raises(RuntimeError, match="layout builder exploded"):
        build_project_detail_layout()
