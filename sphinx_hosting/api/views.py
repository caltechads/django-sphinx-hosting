import os
import tempfile
from pathlib import Path
from typing import Final, List, Optional, Tuple, Type  # noqa: UP035

from django.core.files.storage import FileSystemStorage
from django.db.models import Model
from django.db.models.query import QuerySet
from django_filters import rest_framework as filters
from django_filters.filters import CharFilter, Filter, NumberFilter
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import BaseParser, MultiPartParser
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView

from sphinx_hosting.importers import SphinxPackageImporter
from sphinx_hosting.models import (
    Classifier,
    Project,
    ProjectRelatedLink,
    SphinxImage,
    SphinxPage,
    Version,
)

from .permissions import AddVersionPermission, ChangeProjectPermission
from .serializers import (
    ClassifierSerializer,
    ProjectRelatedLinkSerializer,
    ProjectSerializer,
    SphinxImageSerializer,
    SphinxPageSerializer,
    VersionSerializer,
    VersionUploadSerializer,
)


class ClassifierFilter(filters.FilterSet):
    name: Filter = CharFilter(
        field_name="name",
        lookup_expr="icontains",
        help_text="Filter by classifier name [case insensitive, partial match]",
    )

    class Meta:
        model: Type[Model] = Classifier
        fields: Final[List[str]] = ["name"]


class ClassifierViewSet(viewsets.ModelViewSet):
    permission_classes: Final[List[Type[BasePermission]]] = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]
    serializer_class: Serializer = ClassifierSerializer
    queryset: QuerySet = Classifier.objects.all()
    filterset_class: filters.FilterSet = ClassifierFilter


class ProjectFilter(filters.FilterSet):
    title: Filter = CharFilter(
        lookup_expr="icontains",
        help_text="Filter by project title, [case insensitive, partial match]",
    )
    machine_name: Filter = CharFilter(
        lookup_expr="icontains",
        help_text="Filter by project machine name, [case insensitive, partial match]",
    )
    description: Filter = CharFilter(
        lookup_expr="icontains",
        help_text="Filter by project description, [case insensitive, partial match]",
    )
    classifier: Filter = CharFilter(
        field_name="classifiers__name",
        lookup_expr="icontains",
        help_text=(
            "Filter by project classifier name [case insensitive, partial match]"
        ),
    )

    class Meta:
        model: Type[Model] = Project
        fields: Final[List[str]] = [
            "title",
            "machine_name",
            "description",
            "classifier",
        ]


class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes: Final[List[Type[BasePermission]]] = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]
    serializer_class: Type[Serializer] = ProjectSerializer
    queryset: QuerySet = Project.objects.all()
    filterset_class: Type[filters.FilterSet] = ProjectFilter

    @action(detail=True)
    def latest_version(self, request: Request, pk: Optional[int] = None) -> Response:  # noqa: ARG002, FA100
        project = self.get_object()
        serializer = VersionSerializer(
            project.latest_version, context={"request": request}
        )
        return Response(serializer.data)


class VersionFilter(filters.FilterSet):
    project: Filter = NumberFilter()
    project_title: Filter = CharFilter(
        field_name="project__title",
        lookup_expr="icontains",
        help_text="Filter by project title [case insensitive, partial match]",
    )
    project_machine_name: Filter = CharFilter(
        field_name="project__machine_name",
        lookup_expr="icontains",
        help_text="Filter by project machine name [case insensitive, partial match]",
    )
    project_classifier: Filter = CharFilter(
        field_name="project__classifiers__name",
        lookup_expr="icontains",
        help_text="Filter by project classifier name [case insensitive, partial match]",
    )
    version_number: Filter = CharFilter(
        lookup_expr="iexact",
        help_text="Filter by version number [case insensitive, exact match]",
    )
    sphinx_version: Filter = CharFilter(
        lookup_expr="istartswith",
        help_text=(
            "Filter by Sphinx version [case insensitive, partial match to start "
            "of string]",
        ),
    )
    archived: Filter = filters.BooleanFilter(help_text="Filter by archived status")

    class Meta:
        model: Type[Model] = Version
        fields: Final[List[str]] = [
            "project",
            "project_title",
            "project_machine_name",
            "project_classifier",
            "version",
            "version_number",
            "sphinx_version",
            "archived",
        ]


class VersionViewSet(
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    Users can get, list and delete :py:class:`sphinx_hosting.models.Version` objects,
    but they can't create or update them the normal Django way.
    """

    permission_classes: Final[List[Type[BasePermission]]] = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions | ChangeProjectPermission,
    ]
    serializer_class: Type[Serializer] = VersionSerializer
    queryset: QuerySet = Version.objects.all()
    filterset_class: Type[filters.FilterSet] = VersionFilter


class VersionUploadView(APIView):
    r"""
    The view to use to upload our sphinx tarballs.  It uploads to a
    temporary directory that disappears at the end of this view.

    To upload a file, you must submit as form-data, with a single file key named
    ``file``, with the ``Content-Disposition`` header like so::

        Content-Disposition: attachment;filename=yourdocs.tar.gz

    The filename you pass in the ``Content-Disposition`` header does not matter
    and is not used; set it to whatever you want.

    Example:
        To upload a file with ``curl`` to the endpoint for this view:

        .. code-block:: bash

            curl \
                -XPOST \
                -H "Authorization: Token __THE_API_TOKEN__" \
                -F 'file=@path/to/yourdocs.tar.gz' \
                https://sphinx-hosting.example.com/api/v1/version/import/

    """

    serializer_class: Serializer = VersionUploadSerializer
    permission_classes: Final[List[Type[BasePermission]]] = [
        permissions.IsAuthenticated,
        AddVersionPermission,
    ]
    parser_classes: Final[Tuple[BaseParser, ...]] = (MultiPartParser,)

    def post(self, request: Request) -> Response:
        serializer = VersionUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = FileSystemStorage(tmpdir)
            filename = fs.save("docs.tar.gz", content=serializer.validated_data["file"])
            path = Path(fs.location) / filename
            try:
                version = SphinxPackageImporter().run(filename=str(path), force=True)
            except Project.DoesNotExist as e:
                return Response(
                    {"status": "error", "message": str(e)},
                )
            except Exception:
                # Move the problematic file to a known location so we can
                # inspect it later.
                os.rename(path, "/tmp/uploaded_file")  # noqa: PTH104
                raise

        data = {
            "status": "success",
            "version_id": version.id,
            "project_id": version.project.id,  # type: ignore[attr-defined]
        }
        return Response(data, status=200)


class SphinxPageFilter(filters.FilterSet):
    project: Filter = NumberFilter(
        field_name="version__project", help_text="Filter by project ID"
    )
    project_title: Filter = CharFilter(
        field_name="version__project__title",
        lookup_expr="icontains",
        help_text="Filter by project title [case insensitive, partial match]",
    )
    project_machine_name: Filter = CharFilter(
        field_name="version__project__machine_name",
        lookup_expr="icontains",
        help_text="Filter by project machine name [case insensitive, partial match]",
    )
    project_classifier: Filter = CharFilter(
        field_name="version__project__classifiers__name",
        lookup_expr="icontains",
        help_text="Filter by project classifier name [case insensitive, partial match]",
    )
    version: Filter = NumberFilter(help_text="Filter by version ID")
    version_number: Filter = CharFilter(
        field_name="version__version",
        lookup_expr="iexact",
        help_text="Filter by version number [case insensitive, exact match]",
    )
    archived: Filter = filters.BooleanFilter(
        field_name="version__archived", help_text="Filter by archived status"
    )
    title: Filter = CharFilter(
        lookup_expr="icontains",
        help_text="Filter by page title [case insensitive, partial match]",
    )
    relative_path: Filter = CharFilter(
        lookup_expr="icontains",
        help_text="Filter by page relative path [case insensitive, partial match]",
    )
    sphinx_version: Filter = CharFilter(
        field_name="version__sphinx_version",
        lookup_expr="istartswith",
        help_text=(
            "Filter by Sphinx version [case insensitive, partial match to start of "
            "string]",
        ),
    )

    class Meta:
        model: Type[Model] = SphinxPage
        fields: Final[List[str]] = [
            "project",
            "project_title",
            "project_machine_name",
            "project_classifier",
            "version",
            "version_number",
            "archived",
            "title",
            "relative_path",
            "sphinx_version",
        ]


class SphinxPageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A read-only model set for :py:class:`sphinx_hosting.models.SphinxPage`
    models.  It is purposely read-only because we only want to update pages in
    the source Sphinx project, not here in the database.

    Even for our derived fields that we built out of the source, pages have a
    lot of interdependencies that need to be accounted for while editing.
    """

    permission_classes: Final[List[Type[BasePermission]]] = [
        permissions.IsAuthenticated
    ]
    serializer_class = SphinxPageSerializer
    queryset = SphinxPage.objects.all()
    filterset_class = SphinxPageFilter


class SphinxImageFilter(filters.FilterSet):
    project: Filter = NumberFilter(
        field_name="version__project", help_text="Filter by project ID"
    )
    project_title: Filter = CharFilter(
        field_name="version__project__title",
        lookup_expr="icontains",
        help_text="Filter by project title [case insensitive, partial match]",
    )
    project_machine_name: Filter = CharFilter(
        field_name="version__project__machine_name",
        lookup_expr="icontains",
        help_text="Filter by project machine name [case insensitive, partial match]",
    )
    project_classifier: Filter = CharFilter(
        field_name="version__project__classifiers__name",
        lookup_expr="icontains",
        help_text="Filter by project classifier name [case insensitive, partial match]",
    )
    version: Filter = NumberFilter(help_text="Filter by version ID")
    version_number: Filter = CharFilter(
        field_name="version__version",
        lookup_expr="iexact",
        help_text="Filter by version number [case insensitive, exact match]",
    )
    archived: Filter = filters.BooleanFilter(
        field_name="version__archived", help_text="Filter by archived status"
    )
    sphinx_version: Filter = CharFilter(
        field_name="version__sphinx_version",
        lookup_expr="istartswith",
        help_text=(
            "Filter by Sphinx version [case insensitive, partial match to start "
            "of string]",
        ),
    )
    orig_path: Filter = CharFilter(
        lookup_expr="icontains",
        help_text="Filter by original path [case insensitive, partial match]",
    )

    class Meta:
        model: Type[Model] = SphinxImage
        fields: Final[List[str]] = [
            "project",
            "version",
            "sphinx_version",
            "archived",
            "project_title",
            "project_machine_name",
            "project_classifier",
            "version_number",
            "orig_path",
        ]


class SphinxImageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A read-only model set for :py:class:`sphinx_hosting.models.SphinxImage`
    models.  It is purposely read-only because images are dependent objects of
    :py:class:`sphinx_hosting.models.SphinxPage` instances, and it makes no
    sense to update them independently.
    """

    permission_classes: Final[List[Type[BasePermission]]] = [
        permissions.IsAuthenticated
    ]
    serializer_class: Type[Serializer] = SphinxImageSerializer
    queryset: QuerySet = SphinxImage.objects.all()
    filterset_class: Type[filters.FilterSet] = SphinxImageFilter


class ProjectRelatedLinkFilter(filters.FilterSet):
    title: Filter = CharFilter(
        lookup_expr="icontains",
        help_text="Filter by link title, [case insensitive, partial match]",
    )
    project_title: Filter = CharFilter(
        field_name="project__title",
        lookup_expr="icontains",
        help_text="Filter by project title, [case insensitive, partial match]",
    )
    project_machine_name: Filter = CharFilter(
        field_name="project__machine_name",
        lookup_expr="icontains",
        help_text="Filter by project machine name, [case insensitive, partial match]",
    )
    project_description: Filter = CharFilter(
        field_name="project__description",
        lookup_expr="icontains",
        help_text="Filter by project description, [case insensitive, partial match]",
    )
    project_classifier: Filter = CharFilter(
        field_name="project__classifiers__name",
        lookup_expr="icontains",
        help_text=(
            "Filter by project classifier name [case insensitive, partial match]",
        ),
    )

    class Meta:
        model: Type[Model] = ProjectRelatedLink
        fields: Final[List[str]] = [
            "title",
            "project_title",
            "project_machine_name",
            "project_description",
            "project_classifier",
        ]


class ProjectRelatedLinkViewSet(viewsets.ModelViewSet):
    permission_classes: Final[List[Type[BasePermission]]] = [
        permissions.IsAuthenticated,
        ChangeProjectPermission,
    ]
    serializer_class: Type[Serializer] = ProjectRelatedLinkSerializer
    queryset: QuerySet = ProjectRelatedLink.objects.all()
    filterset_class: Type[filters.FilterSet] = ProjectRelatedLinkFilter
