from typing import Any, Dict

from django.conf import settings
from django.templatetags.static import static


app_settings: Dict[str, Any] = getattr(settings, 'SPHINX_HOSTING_SETTINGS', {})

#: The django path to the logo image.
LOGO_IMAGE: str = static(
    app_settings.get(
        'LOGO_IMAGE',
        'sphinx_hosting/images/logo.jpg',
    )
)
# The URL to associate with the logo image.
LOGO_URL: str = app_settings.get('LOGO_URL', '/')
#: Any valid value for CSS with to control the width of the logo image
LOGO_WIDTH: str = app_settings.get('LOGO_WIDTH', '100%')
#: The name of the site to use in the title of the page.
SITE_NAME: str = app_settings.get('SITE_NAME', 'Sphinx Hosting')
MAX_GLOBAL_TOC_TREE_DEPTH: int = app_settings.get('MAX_GLOBAL_TOC_TREE_DEPTH', 2)
