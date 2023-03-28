from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SphinxHostingApiAppConfig(AppConfig):
    name: str = "sphinx_hosting.api"
    label: str = "sphinxhostingapi"
    verbose_name: str = _("Sphinx Hosting API")  # type: ignore
    default_auto_field: str = "django.db.models.AutoField"
