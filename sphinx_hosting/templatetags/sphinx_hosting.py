from django import template

from ..logging import logger
from ..models import SphinxDocument, SphinxImage

register = template.Library()


@register.simple_tag
def sphinximage_url(pk: int):
    """
    Return the URL to the :py:class:`sphinx_hosting.models.SphinxImage` identified
    by the primary key ``pk``

    Args:
        pk: the primary key of the ``SphinxImage`` object

    Returns:
        The URL for the image file

    """
    return SphinxImage.objects.get(pk=pk).file.url


@register.simple_tag
def sphinxdocument_url(pk: int):
    """
    Return the URL to the :py:class:`sphinx_hosting.models.SphinxDocument` identified
    by the primary key ``pk``

    Args:
        pk: the primary key of the ``SphinxDocument`` object

    Returns:
        The URL for the image file

    """
    url = SphinxDocument.objects.get(pk=pk).file.url.rstrip("/")
    logger.info(f"sphinxdocument_url: {url}")
    return url
