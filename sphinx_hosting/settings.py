from typing import Any, Dict

from django.conf import settings
from django.templatetags.static import static


app_settings: Dict[str, Any] = getattr(settings, 'SPHINX_HOSTING_SETTINGS', {})

LOGO_IMAGE: str = static(
    app_settings.get(
        'LOGO_IMAGE',
        'sphinx_hosting/images/logo.jpg',
    )
)
LOGO_URL: str = app_settings.get('LOGO_URL', '/')
LOGO_WIDTH: str = app_settings.get('LOGO_WIDTH', '100%')
SITE_NAME: str = app_settings.get('SITE_NAME', 'Sphinx Hosting')
MAX_GLOBAL_TOC_TREE_DEPTH: int = app_settings.get('MAX_GLOBAL_TOC_TREE_DEPTH', 2)
