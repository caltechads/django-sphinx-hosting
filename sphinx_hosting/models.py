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

        {project machine_name}/{version}/images/{image basename}

    Args:
        instance: the :py:class:`SphinxImage` object
        filename: the original path to the file

    Returns:
        The properly formatted path to the file
    """
    path = Path(instance.version.project.machine_name) / Path(instance.version.version) / 'images'
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
        help_text=_("""Must be unique.  Set this to the value of "project" in Sphinx's. conf.py""")
    )

    def __str__(self) -> str:  # pylint: disable=invalid-str-returned
        return self.title

    def get_absolute_url(self) -> str:
        return reverse('sphinx_hosting:project--update', args=[self.machine_name])

    class Meta:
        verbose_name: str = _('project')
        verbose_name_plural: str = _('projects')


class Version(TimeStampedModel, models.Model):
    """
    A Version is a specific version of a :py:class:`Project`.  Versions own
    Sphinx pages (:py:class:`SphinxPage`)
    """

    project: FK = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='versions',
        help_text=_('The Project to which this Version belong'),
    )
    version: F = models.CharField(
        'Version',
        max_length=64,
        null=False,
        help_text=_('A version of our project'),
    )

    sphinx_version: F = models.CharField(
        'Sphinx Version',
        max_length=64,
        null=True,
        blank=True,
        default=None,
        help_text=_('The version of Sphinx used to documentation for this set')
    )

    head: FK = models.OneToOneField(
        "SphinxPage",
        on_delete=models.SET_NULL,
        null=True,
        related_name='+',  # disable our related_name for this one
        help_text=_('The top page of the documentation set for this version of our project'),
    )

    def get_absolute_url(self) -> str:
        return reverse(
            'sphinx_hosting:version--detail',
            args=[self.project.machine_name, self.version]
        )


class SphinxPage(TimeStampedModel, models.Model):
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
        '_modules/index': 'Module code'
    }

    version: FK = models.ForeignKey(
        Version,
        on_delete=models.CASCADE,
        related_name='pages',
        help_text=_('The Version to which this page belongs'),
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
    orig_body: F = models.TextField(
        'Body (Original',
        blank=True,
        help_text=_(
            'The original body for the page, extracted from the page JSON. Some pages have no body.'
            'We save this here in case we need to reprocess the body at some later date.'
        ),
    )
    body: F = models.TextField(
        'Body',
        blank=True,
        help_text=_(
            'The body for the page, extracted from the page JSON, and modified to suit us.  '
            'Some pages have no body.'
        ),
    )
    orig_local_toc: F = models.TextField(
        'Local Table of Contents (original)',
        blank=True,
        null=True,
        default=None,
        help_text=_(
            'The original table of contents for headings in this page.'
            'We save this here in case we need to reprocess the table of contents '
            'at some later date.'
        ),
    )
    local_toc: F = models.TextField(
        'Local Table of Contents',
        blank=True,
        null=True,
        default=None,
        help_text=_('Table of Contents for headings in this page, modified to work in our templates'),
    )

    parent: FK = models.ForeignKey(
        "SphinxPage",
        on_delete=models.CASCADE,
        null=True,
        related_name="children",
        help_text=_('The parent page of this page'),
    )

    next_page: FK = models.OneToOneField(
        "SphinxPage",
        on_delete=models.CASCADE,
        null=True,
        related_name="previous_page",
        help_text=_('The next page in the documentation set'),
    )

    def __str__(self) -> str:  # pylint: disable=invalid-str-returned
        return self.relative_path

    def get_absolute_url(self) -> str:
        return reverse(
            'sphinx_hosting:sphinxpage--detail',
            args=[
                self.version.project.machine_name,
                self.version.version,
                self.relative_path
            ]
        )

    class Meta:
        verbose_name = _('sphinx page')
        verbose_name_plural = _('sphinx pages')
        unique_together = ('version', 'relative_path')


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
        verbose_name = _('sphinx image')
        verbose_name_plural = _('sphinx images')
        unique_together = ('version', 'orig_path')
