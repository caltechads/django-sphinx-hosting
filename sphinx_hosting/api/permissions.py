from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView


class ChangeProjectPermission(permissions.BasePermission):
    """
    Check to see if the user can change projects.

    Note:
        This is only for use in on viewsets that are not actually the
        :py:class:`sphinx_hosting.api.models.ProjectViewSet`.  For that one, just use
        :py:class:`restramework.permissions.DjangoModelPermissions`.

    """

    def has_permission(self, request: Request, view: APIView) -> bool:  # noqa: ARG002
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user.has_perm("sphinxhostingcore.change_project"))


class AddVersionPermission(permissions.BasePermission):
    """
    Check to see if the user can add versions.

    Note:
        This is really only useful on
        :py:class:`sphinx_hosting.api.models.VersionUploadView`.

    """

    def has_permission(self, request: Request, view: APIView) -> bool:  # noqa: ARG002
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user.has_perm("sphinxhostingcore.add_version"))
