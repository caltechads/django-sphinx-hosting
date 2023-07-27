from typing import Type, Tuple, Dict, Any

from django.db.models import Model
from rest_framework import serializers
from rest_framework.relations import RelatedField

from sphinx_hosting.models import (
    Classifier,
    Project,
    ProjectRelatedLink,
    SphinxImage,
    SphinxPage,
    Version,
)


class ClassifierSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model: Type[Model] = Classifier
        fields: Tuple[str, ...] = (
            'url',
            'id',
            'name'
        )
        extra_kwargs = {
            'url': {'view_name': 'sphinx_hosting_api:classifier-detail'},
        }


class ProjectSerializer(serializers.HyperlinkedModelSerializer):

    versions: RelatedField = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='sphinx_hosting_api:version-detail'
    )
    classifiers: serializers.Serializer = ClassifierSerializer(many=True)
    related_links: RelatedField = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='sphinx_hosting_api:projectrelatedlink-detail'
    )

    class Meta:
        model: Type[Model] = Project
        read_only_fields: Tuple[str, ...] = ('machine_name', )
        fields: Tuple[str, ...] = (
            'url',
            'id',
            'title',
            'machine_name',
            'description',
            'related_links',
            'classifiers',
            'versions',
        )
        extra_kwargs = {
            'url': {'view_name': 'sphinx_hosting_api:project-detail'},
        }


class ProjectRelatedLinkSerializer(serializers.HyperlinkedModelSerializer):

    project: RelatedField = serializers.HyperlinkedRelatedField(
        queryset=Project.objects.all(),
        view_name='sphinx_hosting_api:project-detail'
    )

    class Meta:
        model: Type[Model] = ProjectRelatedLink
        fields: Tuple[str, ...] = (
            'url',
            'id',
            'title',
            'uri',
            'project',
        )
        extra_kwargs = {
            'url': {'view_name': 'sphinx_hosting_api:projectrelatedlink-detail'},
        }


class VersionSerializer(serializers.HyperlinkedModelSerializer):

    project: RelatedField = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='sphinx_hosting_api:project-detail'
    )
    head: RelatedField = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='sphinx_hosting_api:sphinxpage-detail'
    )
    pages: RelatedField = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='sphinx_hosting_api:sphinxpage-detail'
    )
    images: RelatedField = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='sphinx_hosting_api:sphinximage-detail'
    )

    class Meta:
        model: Type[Model] = Version
        fields: Tuple[str, ...] = (
            'url',
            'id',
            'project',
            'version',
            'sphinx_version',
            'archived',
            'head',
            'pages',
            'images',
        )
        extra_kwargs = {
            'url': {'view_name': 'sphinx_hosting_api:version-detail'},
        }


class VersionUploadSerializer(serializers.Serializer):
    """
    The actual work of importing the file is done in
    :py:class:`sphinx_hosting.api.views.VersionUploadView`.  We're defining our
    :py:meth:`create` and :py:meth:`create` here as NOOP functions to make the
    linters happy because they're abstract in :py:class:`serializers.Serializer`.
    """

    file = serializers.FileField()

    def create(self, validated_data: Dict[str, Any]) -> None:
        pass

    def update(self, instance, validated_data):
        pass

    class Meta:
        fields = ('file', )


class SphinxPageSerializer(serializers.HyperlinkedModelSerializer):

    version: RelatedField = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='sphinx_hosting_api:version-detail'
    )
    parent: RelatedField = serializers.HyperlinkedRelatedField(   # type: ignore
        read_only=True,
        view_name='sphinx_hosting_api:sphinxpage-detail'
    )
    previous_page: RelatedField = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='sphinx_hosting_api:sphinxpage-detail'
    )
    next_page: RelatedField = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='sphinx_hosting_api:sphinxpage-detail'
    )

    class Meta:
        model: Type[Model] = SphinxPage
        fields: Tuple[str, ...] = (
            'url',
            'id',
            'version',
            'title',
            'relative_path',
            'content',
            'orig_body',
            'body',
            'orig_local_toc',
            'local_toc',
            'orig_global_toc',
            'searchable',
            'parent',
            'next_page',
            'previous_page',
        )
        extra_kwargs = {
            'url': {'view_name': 'sphinx_hosting_api:sphinxpage-detail'},
        }


class SphinxImageSerializer(serializers.HyperlinkedModelSerializer):
    version: RelatedField = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='sphinx_hosting_api:version-detail'
    )

    class Meta:
        model: Type[Model] = SphinxImage
        fields: Tuple[str, ...] = (
            'url',
            'id',
            'version',
            'orig_path',
        )
        extra_kwargs = {
            'url': {'view_name': 'sphinx_hosting_api:sphinximage-detail'},
        }
