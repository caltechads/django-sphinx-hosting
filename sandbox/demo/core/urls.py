from typing import Final

from django.urls import path

from .views import (
    SearchNoteCreateView,
    SearchNoteDeleteView,
    SearchNoteDetailView,
    SearchNoteListView,
    SearchNoteUpdateView,
)

#: Application namespace for the demo ``core`` URL patterns.
app_name: Final[str] = "core"

#: CRUD routes for the demo-only ``SearchNote`` model.
urlpatterns = [
    path("notes/", SearchNoteListView.as_view(), name="searchnote--list"),
    path("notes/create/", SearchNoteCreateView.as_view(), name="searchnote--create"),
    path("notes/<int:pk>/", SearchNoteDetailView.as_view(), name="searchnote--detail"),
    path(
        "notes/<int:pk>/update/",
        SearchNoteUpdateView.as_view(),
        name="searchnote--update",
    ),
    path(
        "notes/<int:pk>/delete/",
        SearchNoteDeleteView.as_view(),
        name="searchnote--delete",
    ),
]
