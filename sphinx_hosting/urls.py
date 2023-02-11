from typing import List

from django.urls import path, re_path, URLPattern

from .views import (
    ClassifierViewSet,
    GlobalSphinxPageSearchView,
    ProjectCreateView,
    ProjectDeleteView,
    ProjectListView,
    ProjectUpdateView,
    SphinxPageDetailView,
    VersionDeleteView,
    VersionDetailView,
)
from .wildewidgets import ProjectClassifierSelectorWidget


app_name: str = "sphinx_hosting"

urlpatterns: List[URLPattern] = [
    path('', ProjectListView.as_view(), name='project--list'),
    path('project/', ProjectCreateView.as_view(), name='project--create'),
    path('project/<slug:slug>/', ProjectUpdateView.as_view(), name='project--update'),
    path('project/<slug:slug>/delete/', ProjectDeleteView.as_view(), name='project--delete'),
    path('project/<slug:slug>/', ProjectUpdateView.as_view(), name='project--update'),
    path('project/<slug:project_slug>/<str:version>/', VersionDetailView.as_view(), name='version--detail'),
    path('project/<slug:project_slug>/<str:version>/delete/', VersionDeleteView.as_view(), name='version--delete'),
    re_path(
        r'project/(?P<project_slug>[\w-]+)/(?P<version>[^/]+)/(?P<path>.*)/',
        SphinxPageDetailView.as_view(),
        name='sphinxpage--detail'
    ),
    path('search/', GlobalSphinxPageSearchView.as_view(), name='search')
]
urlpatterns += ClassifierViewSet(url_prefix='lookups', url_namespace=app_name).get_urlpatterns()
urlpatterns += ProjectClassifierSelectorWidget.get_urlpatterns(url_namespace=app_name)
