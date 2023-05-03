from typing import List

from django.urls import path, re_path, URLPattern

from .views import (
    ClassifierViewSet,
    GlobalSphinxPageSearchView,
    ProjectCreateView,
    ProjectDeleteView,
    ProjectDetailView,
    ProjectListView,
    ProjectUpdateView,
    SphinxPageDetailView,
    VersionDeleteView,
    VersionDetailView,
    VersionUploadView
)
from .wildewidgets import ProjectClassifierSelectorWidget


app_name: str = "sphinx_hosting"

urlpatterns: List[URLPattern] = [
    path('', ProjectListView.as_view(), name='project--list'),
    path('project/', ProjectCreateView.as_view(), name='project--create'),
    path('project/<str:slug>/', ProjectDetailView.as_view(), name='project--detail'),
    path('project/<str:slug>/update/', ProjectUpdateView.as_view(), name='project--update'),
    path('project/<str:slug>/upload/', VersionUploadView.as_view(), name='version--upload'),
    path('project/<str:slug>/delete/', ProjectDeleteView.as_view(), name='project--delete'),
    path('project/<str:project_slug>/<str:version>/', VersionDetailView.as_view(), name='version--detail'),
    path('project/<str:project_slug>/<str:version>/delete/', VersionDeleteView.as_view(), name='version--delete'),
    re_path(
        r'project/(?P<project_slug>[-a-zA-Z0-9_.]+)/(?P<version>[^/]+)/(?P<path>.*)/',
        SphinxPageDetailView.as_view(),
        name='sphinxpage--detail'
    ),
    path('search/', GlobalSphinxPageSearchView.as_view(), name='search'),
]
urlpatterns += ClassifierViewSet(url_prefix='lookups', url_namespace=app_name).get_urlpatterns()
urlpatterns += ProjectClassifierSelectorWidget.get_urlpatterns(url_namespace=app_name)
