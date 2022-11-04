from pathlib import Path

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django_extensions.db.models import TimeStampedModel

from .validators import NoHTMLValidator


F = models.Field
M2M = models.ManyToManyField
FK = models.ForeignKey


def sphinx_image_upload_to(instance: "SphinxImage", filename: str) -> str:
    """
    Set our upload path for any images used by our Sphinx documentation to be::

        {project machine_name}/{version}/{image basename}

    Args:
        instance: the :py:class:`SphinxImage` object
        filename: the original path to the file

    Returns:
        The properly formatted path to the file
    """
    path = Path(instance.version.project.name) / Path(instance.version.version)
    path = path / Path(filename).name
    return str(path)


class Project(TimeStampedModel, models.Model):
    """
    A Project is what a set of Sphinx docs describes: an application, a library, etc.

    Projects have versions (:py:class:`Version`) and versions have Sphinx pages
    (:py:class:`SphinxPage`).
    """

    title: F = models.CharField(
        'Project Name',
        help_text=_('The human name for this project'),
        max_length=100
    )
    description: F = models.CharField(
        'Brief Description',
        max_length=256,
        null=True,
        blank=True,
        help_text=_('A brief description of this project'),
        validators=[NoHTMLValidator()]
    )
    machine_name: F = models.SlugField(
        'Machine Name',
        unique=True,
        help_text=_('Used in the URL for the project. Must be unique.')
    )

    def __str__(self) -> str:  # pylint: disable=invalid-str-returned
        return self.title

    def get_absolute_url(self) -> str:
        return reverse('sphinx-hosting:index', kwargs={'machine_name': self.machine_name})

    class Meta:
        verbose_name: str = _('project')
        verbose_name_plural: str = _('projects')


class Version(models.Model):
    """
    A Version is a specific version of a :py:class:`Project`.  Versions own
    Sphinx pages (:py:class:`SphinxPage`)
    """

    project: FK = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='versions'
    )
    version: F = models.CharField(
        'Version',
        help_text=_('A version of our project'),
        max_length=64,
        null=False
    )


class SphinxPage(models.Model):
    """
    A `SphinxPage` is a single page of a set of Sphinx documentation.
    `SphinxPage` objects are owned :py:class:`Version` objects, which are in
    turn owned by :py:class:`Project` objects.
    """

    SPECIAL_TITLES = {
        'genindex': 'General Index',
        'py-modindex': 'Module Index',
        'np-modindex': 'Module Index',
        'search': 'Search',
    }

    version: FK = models.ForeignKey(
        Version,
        on_delete=models.CASCADE,
        related_name='pages'
    )
    relative_path: F = models.CharField(
        'Relative page path',
        help_text=_('The path to the page under our top slug'),
        max_length=255
    )
    content: F = models.TextField(
        'Content',
        help_text=_('The full JSON payload for the page')
    )
    title: F = models.CharField(
        'Title',
        max_length=255,
        help_text=_('Just the title for the page, extracted from the page JSON')
    )
    body: F = models.TextField(
        'Body',
        help_text=_('Just the body for the page, extracted from the page JSON. Some pages have no body.'),
        blank=True,
    )

    def __str__(self) -> str:  # pylint: disable=invalid-str-returned
        return self.relative_path

    def get_absolute_url(self) -> str:
        return reverse(
            'sphinx_hosting:page',
            kwargs={
                'machine_name': self.version.project.machine_name,  # pylint: disable=no-member
                'path': self.relative_path
            }
        )

    class Meta:
        verbose_name = _('sphinx page')
        verbose_name_plural = _('sphinx pages')


class SphinxImage(TimeStampedModel, models.Model):
    """
    A ``SphinxImage`` is an image file referenced in a Sphinx document.  When
    importing documenation packages, we extract all images from the package,
    upload them into Django storage and update the Sphinx HTML in
    :py:attr:`SphinxPage.body` to reference the URL for the uploaded image
    instead of its original url.
    """

    version: FK = models.ForeignKey(
        Version,
        on_delete=models.CASCADE,
        related_name='images',
        help_text=_('The version of our project documentation with which this image is associated')
    )
    orig_path: F = models.CharField(
        _('Original Path'),
        max_length=256,
        help_text=_('The original path to this file in the Sphinx documentation package')
    )
    file: F = models.FileField(
        _('An image file'),
        upload_to=sphinx_image_upload_to,
        help_text=_('The actual image file')
    )

    class Meta:
        unique_together = ('version', 'orig_path')
        verbose_name = _('sphinx image')
        verbose_name_plural = _('sphinx images')
