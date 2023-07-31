from rest_framework import permissions


class ChangeProjectPermission(permissions.BasePermission):
    """
    Check to see if the user can change projects.

    .. note::
        This is only for use in on viewsets that are not actually the
        :py:class:`sphinx_hosting.api.models.ProjectViewSet`.  For that one, just use
        :py:class:`restramework.permissions.DjangoModelPermissions`.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.has_perm('sphinxhostingcore.change_project'):
            return True
        return False


class AddVersionPermission(permissions.BasePermission):
    """
    Check to see if the user can add versions.

    .. note::
        This is really only useful on
        :py:class:`sphinx_hosting.api.models.VersionUploadView`.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.has_perm('sphinxhostingcore.add_version'):
            return True
        return False
