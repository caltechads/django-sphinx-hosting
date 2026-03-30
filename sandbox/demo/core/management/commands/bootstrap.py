from __future__ import annotations

from typing import Any

from demo.logging import logger
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.loader import MigrationLoader


class Command(BaseCommand):
    """
    Run demo migrations and seed baseline data when the database is fresh.

    If ``settings.BOOTSTRAP_ALWAYS_MIGRATE`` is ``True``, always run pending
    migrations on startup.
    """

    def db_is_fresh(self, database: str) -> bool:
        """
        Determine whether the configured database has never run migrations.

        Args:
            database: Django database alias to inspect.

        Returns:
            ``True`` when the database appears to be brand new.

        """
        connection = connections[database]
        loader = MigrationLoader(connection)
        return ("contenttypes", "0001_initial") not in loader.applied_migrations

    def handle(self, *args: str, **options: Any) -> None:
        """
        Apply demo bootstrap tasks for the active environment.

        Args:
            *args: Positional arguments accepted by Django's command runner.

        Keyword Args:
            **options: Command options accepted by Django's command runner.

        Side Effects:
            Runs database migrations and loads baseline demo fixtures.

        """
        del args, options
        logger.info("migrate.start")
        if self.db_is_fresh(DEFAULT_DB_ALIAS):
            call_command("migrate")
            call_command("loaddata", "users")
        elif settings.BOOTSTRAP_ALWAYS_MIGRATE:
            call_command("migrate")
        logger.info("migrate.end")
