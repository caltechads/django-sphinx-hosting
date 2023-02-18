from typing import List, Union

from django.urls import include, path, re_path, URLPattern, URLResolver

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView
)
from rest_framework import routers

from .views import (
    ClassifierViewSet,
    ProjectViewSet,
    VersionViewSet,
    SphinxPageViewSet,
    SphinxImageViewSet,
    VersionUploadView
)

app_name: str = "sphinx_hosting_api"
router: routers.BaseRouter = routers.DefaultRouter()

# Users
router.register(r'classifiers', ClassifierViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'versions', VersionViewSet)
router.register(r'pages', SphinxPageViewSet)
router.register(r'images', SphinxImageViewSet)

urlpatterns: List[Union[URLPattern, URLResolver]] = [
    path('', include(router.urls)),
    path('version/import/', VersionUploadView.as_view(), name='version-import'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'schema/swagger-ui/',
        SpectacularSwaggerView.as_view(url_name='sphinx_hosting_api:schema'),
        name='swagger-ui'
    ),
    path(
        'schema/redoc/',
        SpectacularRedocView.as_view(url_name='sphinx_hosting_api:schema'),
        name='redoc'
    ),
]
