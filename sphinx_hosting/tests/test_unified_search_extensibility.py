# ruff: noqa: S101, SLF001

from __future__ import annotations

from dataclasses import dataclass
from http import HTTPStatus
from typing import Any

import pytest
from demo.core.models import SearchNote
from django.http import HttpResponse
from django.test import RequestFactory, override_settings
from haystack import connections
from haystack.models import SearchResult
from wildewidgets import Block

from sphinx_hosting.global_search_view import (
    GlobalSphinxPageSearchView,
    _apply_global_search_facets,
)
from sphinx_hosting.models import Classifier, Project, SphinxPage, Version
from sphinx_hosting.search_result_renderers import (
    _resolve_search_result_renderers,
    build_search_result_widget,
    get_search_result_models,
    get_search_result_renderers,
)
from sphinx_hosting.wildewidgets.search import SearchResultBlock
from sphinx_hosting.wildewidgets.unified_search import UnifiedSearchResultWidget

RENDERER_CALLS: list[tuple[Any, Any, Any, Any]] = []
INVALID_RENDERER = 3


@dataclass
class DummyUser:
    def has_perm(self, permission: str) -> bool:
        del permission
        return False


def render_search_note_marker(*, result, request, user, view):
    RENDERER_CALLS.append((result, request, user, view))
    widget = Block("Host note")
    widget.title = "Host Search Note"
    return widget


def render_search_note_raises(*, result, request, user, view):
    del result, request, user, view
    msg = "renderer exploded"
    raise RuntimeError(msg)


@dataclass
class DummyForm:
    queryset: Any
    cleaned_data: dict[str, str]

    def search(self):
        return self.queryset


class FakeSearchQuerySet:
    def __init__(self):
        self.model_calls: list[tuple[type[Any], ...]] = []
        self.narrow_calls: list[str] = []

    def models(self, *models):
        self.model_calls.append(models)
        return self

    def narrow(self, query):
        self.narrow_calls.append(query)
        return self


@pytest.fixture(autouse=True)
def clear_search_renderer_state():
    _resolve_search_result_renderers.cache_clear()
    RENDERER_CALLS.clear()
    backend = connections["default"].get_backend()
    backend.clear(models=[SphinxPage, SearchNote])
    yield
    _resolve_search_result_renderers.cache_clear()
    RENDERER_CALLS.clear()
    backend.clear(models=[SphinxPage, SearchNote])


def _create_search_page(
    *,
    title: str = "Built-in Result",
    body: str = "<p>Alpha built-in result body</p>",
    classifier_name: str | None = None,
) -> SphinxPage:
    suffix = Project.objects.count() + 1
    project = Project.objects.create(
        title=f"{title} Project",
        machine_name=f"{title.lower().replace(' ', '-')}-project-{suffix}",
    )
    if classifier_name is not None:
        classifier = Classifier.objects.create(name=classifier_name)
        project.classifiers.add(classifier)
    version = Version.objects.create(project=project, version="1.0.0")
    page = SphinxPage.objects.create(
        version=version,
        relative_path="index",
        content="{}",
        title=title,
        orig_body=body,
        body=body,
        searchable=True,
    )
    version.head = page
    version.save()
    project.latest_version = version
    project.save()
    return page


def _create_search_note(
    *,
    project: Project | None = None,
    title: str = "Host Result",
    body: str = "Alpha host result body",
    classifier_name: str | None = None,
) -> SearchNote:
    if project is None:
        suffix = Project.objects.count() + 1
        project = Project.objects.create(
            title=f"{title} Project",
            machine_name=f"{title.lower().replace(' ', '-')}-project-{suffix}",
        )
    note = SearchNote.objects.create(title=title, body=body, project=project)
    if classifier_name is not None:
        classifier, _ = Classifier.objects.get_or_create(name=classifier_name)
        note.classifiers.add(classifier)
        project.classifiers.add(classifier)
    return note


def _make_result(instance: Any, *, score: float = 1.0) -> SearchResult:
    model = instance._meta
    return SearchResult(model.app_label, model.model_name, str(instance.pk), score)


def _build_view(request) -> GlobalSphinxPageSearchView:
    view = GlobalSphinxPageSearchView()
    view.request = request
    return view


@override_settings(SPHINX_HOSTING_SETTINGS={})
def test_search_result_renderers_default_to_empty():
    assert get_search_result_renderers() == {}
    assert get_search_result_models() == ()


@override_settings(SPHINX_HOSTING_SETTINGS={"SEARCH_RESULT_RENDERERS": []})
def test_search_result_renderers_requires_dict():
    with pytest.raises(TypeError, match="must be a dict"):
        get_search_result_renderers()


@override_settings(SPHINX_HOSTING_SETTINGS={"SEARCH_RESULT_RENDERERS": {3: "foo.bar"}})
def test_search_result_renderers_requires_string_model_labels():
    with pytest.raises(TypeError, match="keys must be Django model labels as strings"):
        get_search_result_renderers()


@override_settings(
    SPHINX_HOSTING_SETTINGS={"SEARCH_RESULT_RENDERERS": {"core.SearchNote": 3}}
)
def test_search_result_renderers_requires_string_dotted_paths():
    with pytest.raises(TypeError, match="must be a dotted-path string"):
        get_search_result_renderers()


@override_settings(
    SPHINX_HOSTING_SETTINGS={"SEARCH_RESULT_RENDERERS": {"core.MissingNote": "foo.bar"}}
)
def test_search_result_renderers_reject_unknown_model_labels():
    with pytest.raises(LookupError, match="does not resolve to a Django model"):
        get_search_result_renderers()


@override_settings(
    SPHINX_HOSTING_SETTINGS={
        "SEARCH_RESULT_RENDERERS": {
            "users.User": (
                "sphinx_hosting.tests.test_unified_search_extensibility."
                "render_search_note_marker"
            )
        }
    }
)
def test_search_result_renderers_require_registered_search_indexes():
    with pytest.raises(LookupError, match="registered Haystack SearchIndex"):
        get_search_result_renderers()


@override_settings(
    SPHINX_HOSTING_SETTINGS={
        "SEARCH_RESULT_RENDERERS": {
            "core.SearchNote": (
                "sphinx_hosting.tests.test_unified_search_extensibility."
                "INVALID_RENDERER"
            )
        }
    }
)
def test_search_result_renderers_require_callable_targets():
    with pytest.raises(TypeError, match="which is not callable"):
        get_search_result_renderers()


@override_settings(
    SPHINX_HOSTING_SETTINGS={
        "SEARCH_RESULT_RENDERERS": {
            "core.SearchNote": (
                "sphinx_hosting.tests.test_unified_search_extensibility."
                "render_search_note_marker"
            )
        }
    }
)
def test_search_result_models_return_registered_host_models():
    assert get_search_result_models() == (SearchNote,)


@pytest.mark.django_db
def test_apply_global_search_facets_uses_exact_narrow_queries():
    queryset = FakeSearchQuerySet()
    request = RequestFactory().get(
        "/search/",
        {"project_id": "17", "classifiers": 'alpha "beta"'},
    )

    filtered_queryset, facets = _apply_global_search_facets(queryset, request)

    assert filtered_queryset is queryset
    assert queryset.narrow_calls == [
        'project_id_exact:"17"',
        'classifiers_exact:"alpha \\"beta\\""',
    ]
    assert facets == {"project_id": ["17"], "classifiers": ['alpha "beta"']}


@pytest.mark.django_db
@override_settings(
    SPHINX_HOSTING_SETTINGS={
        "SEARCH_RESULT_RENDERERS": {
            "core.SearchNote": (
                "sphinx_hosting.tests.test_unified_search_extensibility."
                "render_search_note_marker"
            )
        }
    }
)
def test_global_search_view_constrains_models_and_facets():
    queryset = FakeSearchQuerySet()
    request = RequestFactory().get(
        "/search/",
        {"q": "alpha", "project_id": "12", "classifiers": "docs"},
    )
    request.user = DummyUser()
    view = _build_view(request)
    view.search_field = "q"
    view.get_context_data = lambda **kwargs: kwargs
    view.render_to_response = lambda context: HttpResponse(str(context))
    form = DummyForm(queryset=queryset, cleaned_data={"q": "alpha"})

    response = view.form_valid(form)

    assert response.status_code == HTTPStatus.OK
    assert queryset.model_calls == [(SphinxPage, SearchNote)]
    assert queryset.narrow_calls == [
        'project_id_exact:"12"',
        'classifiers_exact:"docs"',
    ]
    assert view.object_list is queryset
    assert view.facets == {"project_id": ["12"], "classifiers": ["docs"]}


@pytest.mark.django_db
def test_build_search_result_widget_uses_builtin_sphinxpage_renderer():
    page = _create_search_page()
    request = RequestFactory().get("/search/?q=alpha")
    request.user = DummyUser()
    view = _build_view(request)

    widget = build_search_result_widget(
        result=_make_result(page),
        request=request,
        user=request.user,
        view=view,
    )

    assert isinstance(widget, SearchResultBlock)


@pytest.mark.django_db
@override_settings(
    SPHINX_HOSTING_SETTINGS={
        "SEARCH_RESULT_RENDERERS": {
            "core.SearchNote": (
                "sphinx_hosting.tests.test_unified_search_extensibility."
                "render_search_note_marker"
            )
        }
    }
)
def test_unified_search_result_widget_dispatches_to_host_renderer():
    note = _create_search_note()
    request = RequestFactory().get("/search/?q=alpha")
    request.user = DummyUser()
    view = _build_view(request)

    widget = UnifiedSearchResultWidget(
        object=_make_result(note),
        request=request,
        view=view,
    )

    assert len(RENDERER_CALLS) == 1
    assert RENDERER_CALLS[0][0].pk == str(note.pk)
    assert widget.blocks[0].title == "Host Search Note"


@pytest.mark.django_db
@override_settings(
    SPHINX_HOSTING_SETTINGS={
        "SEARCH_RESULT_RENDERERS": {
            "core.SearchNote": (
                "sphinx_hosting.tests.test_unified_search_extensibility."
                "render_search_note_raises"
            )
        }
    }
)
def test_search_result_renderer_exception_propagates():
    note = _create_search_note()
    request = RequestFactory().get("/search/?q=alpha")
    request.user = DummyUser()
    view = _build_view(request)

    with pytest.raises(RuntimeError, match="renderer exploded"):
        build_search_result_widget(
            result=_make_result(note),
            request=request,
            user=request.user,
            view=view,
        )
