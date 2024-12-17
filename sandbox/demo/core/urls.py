from typing import Final

from django.urls import include, path

from sphinx_hosting import urls as sphinx_hosting_urls

# These URLs are loaded by demo/urls.py.
app_name: Final[str] = "core"

urlpatterns = [
    path("", include(sphinx_hosting_urls, namespace="sphinx_hosting")),
]
