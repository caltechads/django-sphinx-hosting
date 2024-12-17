from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from wildewidgets import WildewidgetDispatch

from sphinx_hosting import urls as sphinx_hosting_urls
from sphinx_hosting.api import urls as sphinx_hosting_api_urls

urlpatterns = [
    path("", include(sphinx_hosting_urls, namespace="sphinx_hosting")),
    path("api/v1/", include(sphinx_hosting_api_urls, namespace="sphinx_hosting_api")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("admin/", include(admin.site.urls[:2], namespace=admin.site.name)),
    path("wildewidgets_json", WildewidgetDispatch.as_view(), name="wildewidgets_json"),
]


if settings.ENABLE_DEBUG_TOOLBAR:
    import debug_toolbar

    urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))
