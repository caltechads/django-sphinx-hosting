import fnmatch
import re
from typing import Optional, Type  # noqa: UP035

import semver
from django.db.models import Model
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .logging import logger
from .models import Version
from .search_indexes import SphinxPageIndex
from .settings import EXCLUDE_FROM_LATEST


@receiver(pre_delete, sender=Version)
def set_new_latest_version(sender: Type[Model], instance: Version, **kwargs):  # noqa: ARG001
    """
    Before we delete a version, we need to set a new latest version for the
    project to which this version belongs, if it was the latest version.

    If we do set a new latest version, reindex the project in our search index.

    Args:
        sender: The model class.
        instance: The version whose pages we want to delete.

    Keyword Args:
        **kwargs: Arbitrary keyword arguments. (unused)

    """
    logger.info(
        "project.latest_version.deleting project_id=%s project_title=%s "
        "old_latest=%s version_id=%s",
        instance.project.pk,  # type: ignore[attr-defined]
        instance.project.title,  # type: ignore[attr-defined]
        instance.version,
        instance.pk,
    )
    if instance.is_latest:
        # Get the next highest version number that isn't the one we're deleting
        # We should get a list of 2-tuples like [(1, '1.0.0'), (2, '1.1.0'), ...]
        versions_qs = instance.project.versions.exclude(pk=instance.pk).values_list(  # type: ignore[attr-defined]
            "id", "version"
        )
        # Compile up our globs list
        # sort them by version number, and then get the last one.
        versions: list = []
        for version_id, version_str in versions_qs:
            if not any(
                fnmatch.fnmatch(version_str, glob) for glob in EXCLUDE_FROM_LATEST
            ):
                try:
                    ver = semver.VersionInfo.parse(version_str)
                except ValueError:
                    logger.warning(
                        "project.version.invalid-semver project_id=%s project_title=%s "
                        "version=%s version_id=%s",
                        instance.project.pk,  # type: ignore[attr-defined]
                        instance.project.title,  # type: ignore[attr-defined]
                        version_str,
                        version_id,
                    )
                    continue
                versions.append((version_id, ver))
        versions.sort(key=lambda x: x[1])
        if len(versions) > 1:
            new_latest = Version.objects.get(pk=versions[-1][0])
        elif len(versions_qs) > 1:
            versions = []
            for version_id, version_str in versions_qs:
                try:
                    ver = semver.VersionInfo.parse(version_str)
                except ValueError:
                    # Try to fix our old non-semver versions
                    _version_str = re.sub(
                        r"\.((dev|alpha|beta|rc)\d+)$", "-\1", version_str
                    )
                    ver = semver.VersionInfo.parse(_version_str)
                versions.append((version_id, ver))
            new_latest = Version.objects.get(pk=versions[-1][0])
        else:
            new_latest = None
        # Purge the old latest version from the search index
        SphinxPageIndex().remove_version(instance)
        # If there are no versions left, new_latest will be None, which is fine
        instance.project.latest_version = new_latest  # type: ignore[attr-defined]
        instance.project.save()  # type: ignore[attr-defined]
        # Log the new latest version
        version: Optional[str] = None  # noqa: FA100
        if new_latest:
            version = new_latest.version
            # Index the new latest version
            SphinxPageIndex().reindex_project(instance.project)  # type: ignore[arg-type]
        logger.info(
            "project.latest_version.updated project_id=%s project_title=%s "
            "new_latest=%s version_id=%s",
            instance.project.pk,  # type: ignore[attr-defined]
            instance.project.title,  # type: ignore[attr-defined]
            version,
            new_latest.pk if new_latest else None,
        )
