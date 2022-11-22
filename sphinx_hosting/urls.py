from typing import List

from django.urls import path, URLPattern

from .views import (
    ProjectCreateView,
    ProjectDeleteView,
    ProjectListView,
    ProjectUpdateView,
    SphinxPageDetailView,
    VersionDeleteView,
    VersionDetailView,
)


app_name: str = "sphinx_hosting"

urlpatterns: List[URLPattern] = [
    path('', ProjectListView.as_view(), name='project--list'),
    path('project/', ProjectCreateView.as_view(), name='project--create'),
    path('project/<slug:slug>/', ProjectUpdateView.as_view(), name='project--update'),
    path('project/<slug:slug>/delete/', ProjectDeleteView.as_view(), name='project--delete'),
    path('project/<slug:slug>/', ProjectUpdateView.as_view(), name='project--update'),
    path('project/<slug:project_slug>/<str:version>/', VersionDetailView.as_view(), name='version--detail'),
    path('project/<slug:project_slug>/<str:version>/delete/', VersionDeleteView.as_view(), name='version--delete'),
    path(
        'project/<slug:project_id>/<str:version>/<str:path>/',
        SphinxPageDetailView.as_view(),
        name='sphinxpage--detail'
    ),
]
