import re
from typing import cast

from django.core.management.base import BaseCommand
from django.utils.text import slugify
import lxml.html
from rich.tree import Tree

from sphinx_hosting.models import SphinxPage


class Command(BaseCommand):
    """
    **Usage**: ``./manage.py fix_broken_hrefs``

    This is a one-shot command to fix broken hrefs from imported data that
    used ``django-sphinx-hosting`` version 1.1.5 or earlier.  This command
    fixes internal hrefs that were imported to be template tags which resolve
    the proper page at render time.

    Print the page tree for a :py:class:`Version`
    """

    def _fix_link_hrefs(self, body: str, project_machine_name: str, version: str) -> str:
        """
        Given an HTML body of a Sphinx page, update the ``<a href="path">``
        references to be absolute.  If we don't do this, any links on the
        index page the version will be relative to the index page, instead of
        being relative to the root of the docs, and won't work.

        Args:
            body: the HTML body of a Sphinx document

        Returns:
            ``body`` with its ``<a>`` urls and updated
        """
        html = lxml.html.fromstring(body)
        links = html.cssselect('a.reference.internal')
        for link in links:
            href = link.attrib['href']
            if href.endswith('/'):
                href = href[:-1]
            link.attrib['href'] = "{{% url 'sphinx_hosting:sphinxpage--detail' '{}' '{}' '{}' %}}".format(
                project_machine_name,
                version,
                href
            )
        body = lxml.html.tostring(html).decode('utf-8')
        # Unescape our template tags after lxml has converted our {% %}
        # to entities.  The pattern we're looking for looks something
        # like this::
        #
        #     %7B%%20sphinximage_url%2026%20%%7D
        body = re.sub(r'%7B%%20', r'{% ', body)
        body = re.sub(r"url%20'", r"url '", body)
        body = re.sub(r"'%20'", r"' '", body)
        body = re.sub(r"'%20%%7D", r"' %}", body)
        return body

    def handle(self, *args, **options) -> None:
        for page in SphinxPage.objects.all():
            if page.relative_path not in SphinxPage.SPECIAL_PAGES:
                if not page.body:
                    continue
                page.body = self._fix_link_hrefs(
                    page.body,
                    page.version.project.machine_name,
                    page.version.version
                )
                page.save()
                print(
                    f'Fixed page {page.version.project.machine_name}-{page.version.version}:'
                    '{page.title}'
                )
