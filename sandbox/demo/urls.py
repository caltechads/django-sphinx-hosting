from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from wildewidgets import WildewidgetDispatch

from .core import urls as core_urls


urlpatterns = [
    path('', include(core_urls, namespace='core')),
    path('admin/', include(admin.site.urls[:2], namespace=admin.site.name)),
    path('wildewidgets_json', WildewidgetDispatch.as_view(), name='wildewidgets_json'),
]


if settings.ENABLE_DEBUG_TOOLBAR:
    import debug_toolbar
    urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))
