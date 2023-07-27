import os
import tempfile
from typing import List, Type, Optional

from django.core.files.storage import FileSystemStorage
from django.db.models import Model
from django_filters import rest_framework as filters
from django_filters.filters import Filter, CharFilter, NumberFilter
from rest_framework import viewsets, permissions, mixins
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView

from sphinx_hosting.models import (
    Classifier,
    Project,
    ProjectRelatedLink,
    Version,
    SphinxPage,
    SphinxImage,
)
from sphinx_hosting.importers import SphinxPackageImporter

from .serializers import (
    ClassifierSerializer,
    ProjectSerializer,
    ProjectRelatedLinkSerializer,
    VersionSerializer,
    VersionUploadSerializer,
    SphinxPageSerializer,
    SphinxImageSerializer,
)


class ClassifierFilter(filters.FilterSet):

    name: Filter = CharFilter(
        field_name="name",
        lookup_expr="icontains",
        help_text="Filter by classifier name [case insensitive, partial match]",
    )

    class Meta:
        model: Type[Model] = Classifier
        fields: List[str] = ["name"]


class ClassifierViewSet(viewsets.ModelViewSet):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClassifierSerializer
    queryset = Classifier.objects.all()
    filterset_class = ClassifierFilter


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
        help_text="Filter by project classifier name [case insensitive, partial match]]",
    )

    class Meta:
        model: Type[Model] = Project
        fields: List[str] = ["title", "machine_name", "description", "classifier"]


class ProjectViewSet(viewsets.ModelViewSet):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    filterset_class = ProjectFilter

    @action(detail=True)
    def latest_version(self, request: Request, pk: Optional[int] = None) -> Response:
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
        help_text="Filter by Sphinx version [case insensitive, partial match to start of string]",
    )
    archived: Filter = filters.BooleanFilter(help_text="Filter by archived status")

    class Meta:
        model: Type[Model] = Version
        fields: List[str] = [
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

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VersionSerializer
    queryset = Version.objects.all()
    filterset_class = VersionFilter


class VersionUploadView(APIView):
    """
    This is the view to use to upload our sphinx tarballs.  It uploads to a
    temporary directory that disappears at the end of this view.

    To upload a file, you must submit as form-data, with a single file key named
    ``file``, with the ``Content-Disposition`` header like so::

        Content-Disposition: attachment;filename=yourdocs.tar.gz

    The filename you pass in the ``Content-Disposition`` header does not matter
    and is not used; set it to whatever you want.

    Example:

        To upload a file with ``curl`` to the endpoint for this view::

            curl \\
                -XPOST \\
                -H "Authorization: Token __THE_API_TOKEN__" \\
                -F 'file=@path/to/yourdocs.tar.gz' \\
                https://sphinx-hosting.example.com/api/v1/version/import/
    """

    serializer_class = VersionUploadSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser,)

    def post(self, request: Request) -> Response:
        serializer = VersionUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = FileSystemStorage(tmpdir)
            filename = fs.save("docs.tar.gz", content=serializer.validated_data["file"])
            path = os.path.join(fs.location, filename)
            try:
                version = SphinxPackageImporter().run(filename=path, force=True)
            except Project.DoesNotExist as e:
                return Response(
                    {"status": "error", "message": str(e)},
                )
            except Exception:
                os.rename(path, "/tmp/uploaded_file")
                raise

        data = {
            "status": "success",
            "version_id": version.id,
            "project_id": version.project.id,
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
        help_text="Filter by Sphinx version [case insensitive, partial match to start of string]",
    )

    class Meta:
        model: Type[Model] = SphinxPage
        fields: List[str] = [
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
    This is a read-only model set for
    :py:class:`sphinx_hosting.models.SphinxPage` models.  It is purposely
    read-only because we only want to update pages in the source Sphinx project,
    not here in the database.

    Even for our derived fields that we built out of the source, pages have a
    lot of interdependencies that need to be accounted for while editing.
    """

    permission_classes = [permissions.IsAuthenticated]
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
        help_text="Filter by Sphinx version [case insensitive, partial match to start of string]",
    )
    orig_path: Filter = CharFilter(
        lookup_expr="icontains",
        help_text="Filter by original path [case insensitive, partial match]",
    )

    class Meta:
        model: Type[Model] = SphinxImage
        fields: List[str] = [
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
    This is a read-only model set for
    :py:class:`sphinx_hosting.models.SphinxImage` models.  It is purposely
    read-only because images are dependent objects of
    :py:class:`sphinx_hosting.models.SphinxPage` instances, and it makes no
    sense to update them independently.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SphinxImageSerializer
    queryset = SphinxImage.objects.all()
    filterset_class = SphinxImageFilter


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
        help_text="Filter by project classifier name [case insensitive, partial match]]",
    )

    class Meta:
        model: Type[Model] = ProjectRelatedLink
        fields: List[str] = [
            "title",
            "project_title",
            "project_machine_name",
            "project_description",
            "project_classifier"
        ]


class ProjectRelatedLinkViewSet(viewsets.ModelViewSet):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProjectRelatedLinkSerializer
    queryset = ProjectRelatedLink.objects.all()
    filterset_class = ProjectRelatedLinkFilter
