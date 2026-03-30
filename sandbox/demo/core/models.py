from __future__ import annotations

from typing import Any, cast

from django.db import models
from django.urls import reverse
from django_extensions.db.models import TimeStampedModel

#: Alias for standard Django model fields.
F = models.Field
#: Alias for Django foreign-key fields.
FK = models.ForeignKey
#: Alias for Django many-to-many fields.
M2M = models.ManyToManyField


class SearchNote(TimeStampedModel):
    """
    Demo-only searchable content used to exercise unified global search.

    ``SearchNote`` instances belong to one ``Project`` and may also be tagged
    with zero or more ``Classifier`` objects so the demo app can verify that
    host-model search hits participate in the same facet filters as built-in
    ``SphinxPage`` results.

    """

    #: The visible title for this searchable note.
    title: F = models.CharField(max_length=200)
    #: The full searchable body text for this note.
    body: F = models.TextField()
    #: The project associated with this searchable note.
    project: FK = models.ForeignKey(
        "sphinxhostingcore.Project",
        on_delete=models.CASCADE,
        related_name="+",
    )
    #: Optional classifiers that should participate in unified-search facets.
    classifiers: M2M = models.ManyToManyField(
        "sphinxhostingcore.Classifier",
        related_name="+",
        blank=True,
    )

    def __str__(self) -> str:
        """
        Return the visible label for this note.

        Returns:
            The note title.

        """
        return self.title

    def get_absolute_url(self) -> str:
        """
        Return the detail page for this note.

        Returns:
            The URL for the note detail view.

        """
        return reverse("core:searchnote--detail", args=[self.pk])

    def get_update_url(self) -> str:
        """
        Return the update page for this note.

        Returns:
            The URL for the note update view.

        """
        return reverse("core:searchnote--update", args=[self.pk])

    def get_delete_url(self) -> str:
        """
        Return the delete-confirmation page for this note.

        Returns:
            The URL for the note delete view.

        """
        return reverse("core:searchnote--delete", args=[self.pk])

    def get_project_url(self) -> str:
        """
        Return the associated project detail page.

        Returns:
            The URL for the linked project detail view.

        """
        project = cast("Any", self.project)
        return reverse(
            "sphinx_hosting:project--detail",
            args=[cast("str", project.machine_name)],
        )

    class Meta:
        verbose_name = "search note"
        verbose_name_plural = "search notes"
        ordering = ("title",)
