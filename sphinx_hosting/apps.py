from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SphinxHostingAppConfig(AppConfig):
    name: str = "sphinx_hosting"
    label: str = "sphinxhostingcore"
    verbose_name = _("Sphinx Hosting core")
    default_auto_field: str = "django.db.models.AutoField"
    ready_is_done: bool = False

    def ready(self):
        """
        This function runs as soon as the app is loaded. It loads our signal receivers.
        """
        # As suggested by the Django docs, we need to make absolutely certain
        # that this code runs only once.
        if not self.ready_is_done:
            # See https://docs.djangoproject.com/en/dev/topics/signals/#connecting-receiver-functions, in the
            # "Where should this code live?" section, for why this import is
            # inside CoreConfig.ready().  To disable model change logging,
            # comment out this import.
            from . import signals  # pylint: disable=unused-import,import-outside-toplevel  # noqa:F401
            self.ready_is_done = True
        else:
            print(f"{self.__class__.__name__}.ready() executed multiple times! It is skipped on subsequent runs.")
