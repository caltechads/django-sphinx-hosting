from typing import Dict, Any
from django.conf import settings
from django.http.request import HttpRequest
from django.templatetags.static import static


def theme(request: HttpRequest) -> Dict[str, Any]:
    """
    Inject our theme variables into our templates.
    """
    theme_settings: Dict[str, Any] = getattr(settings, 'THEME_SETTINGS', {})
    return {
        # Header
        'APPLE_TOUCH_ICON': theme_settings.get('APPLE_TOUCH_ICON', static('theme/images/apple-touch-icon.png')),
        'FAVICON_32': theme_settings.get('FAVICON_32', static('theme/images/favicon-32x32.png')),
        'FAVICON_16': theme_settings.get('FAVICON_16', static('theme/images/favicon-16x16.png')),
        'FAVICON': theme_settings.get('FAVICON', static('theme/images/favicon.ico')),
        'SITE_WEBMANIFEST': theme_settings.get('ORGANIZATION_NAME', static('theme/images/site.webmanifest')),

        # Footer
        'ORGANIZATION_LINK': theme_settings.get('ORGANIZATION_LINK', 'https://google.com'),
        'ORGANIZATION_NAME': theme_settings.get('ORGANIZATION_NAME', 'Organization Name'),
        'ORGANIZATION_ADDRESS': theme_settings.get('ORGANIZATION_ADDRESS', 'Organization Address'),
        'COPYWRITE_ORGANIZATION': theme_settings.get('COPYRIGHT_ORGANIZATION', 'Copyright Organization'),
        'FOOTER_LINKS': theme_settings.get('FOOTER_LINKS', [])
    }
