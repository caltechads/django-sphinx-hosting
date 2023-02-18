from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SphinxHostingAppConfig(AppConfig):
    name: str = "sphinx_hosting"
    label: str = "sphinxhostingcore"
    verbose_name = _("Sphinx Hosting core")
    default_auto_field: str = "django.db.models.AutoField"
