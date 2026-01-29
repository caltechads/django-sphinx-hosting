from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SphinxHostingApiAppConfig(AppConfig):
    """
    The app config for the sphinx_hosting.api app.
    """

    #: The name of the app.
    name: str = "sphinx_hosting.api"
    #: The label of the app.
    label: str = "sphinxhostingapi"
    #: The verbose name of the app.
    verbose_name: str = _("Sphinx Hosting API")  # type: ignore[assignment]
    #: The default auto field for the app.
    default_auto_field: str = "django.db.models.AutoField"
