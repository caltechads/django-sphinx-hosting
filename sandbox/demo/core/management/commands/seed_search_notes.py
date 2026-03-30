from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand

from sphinx_hosting.models import Classifier, Project

from ...models import SearchNote
from ...search_note_seed import SEARCH_NOTE_SEEDS


class Command(BaseCommand):
    """
    Create or update the demo ``SearchNote`` records used by the sandbox app.
    """

    #: Help text shown in Django's management-command listings.
    help = "Seed the demo app with SearchNote records derived from repository docs."

    def handle(self, *args: str, **options: Any) -> None:
        """
        Upsert the curated demo ``SearchNote`` records and related metadata.

        Args:
            *args: Positional arguments accepted by Django's command runner.

        Keyword Args:
            **options: Command options accepted by Django's command runner.

        Side Effects:
            Creates or updates demo ``Project``, ``Classifier``, and
            ``SearchNote`` records.

        """
        del args, options
        created = 0
        updated = 0
        for seed in SEARCH_NOTE_SEEDS:
            project, _ = Project.objects.get_or_create(
                machine_name=seed.project_machine_name,
                defaults={"title": seed.project_title},
            )
            if project.title != seed.project_title:
                project.title = seed.project_title
                project.save(update_fields=["title"])

            classifiers = [
                Classifier.objects.get_or_create(name=name)[0]
                for name in seed.classifiers
            ]
            if classifiers:
                project.classifiers.add(*classifiers)

            note, was_created = SearchNote.objects.update_or_create(
                title=seed.title,
                defaults={
                    "body": seed.body,
                    "project": project,
                },
            )
            note.classifiers.set(classifiers)
            if was_created:
                created += 1
            else:
                updated += 1

        message = (
            f"Seeded {created + updated} SearchNote records "
            f"({created} created, {updated} updated)."
        )
        self.stdout.write(self.style.SUCCESS(message))
