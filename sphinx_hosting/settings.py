from typing import Any

from django.conf import settings
from django.templatetags.static import static

app_settings: dict[str, Any] = getattr(settings, "SPHINX_HOSTING_SETTINGS", {})

#: The setting key for extra static navigation items.
EXTRA_MENU_ITEMS_SETTING: str = "EXTRA_MENU_ITEMS"
#: The setting key for conditional menu item builder callables.
MENU_ITEM_BUILDERS_SETTING: str = "MENU_ITEM_BUILDERS"
#: The setting key for the navbar class override.
NAVBAR_CLASS_SETTING: str = "NAVBAR_CLASS"
#: The setting key for project-detail layout builder callables.
PROJECT_DETAIL_LAYOUT_BUILDERS_SETTING: str = "PROJECT_DETAIL_LAYOUT_BUILDERS"

#: The django path to the logo image.
LOGO_IMAGE: str = static(
    app_settings.get(
        "LOGO_IMAGE",
        "sphinx_hosting/images/logo.jpg",
    )
)
#: The URL to associate with the logo image.
LOGO_URL: str = app_settings.get("LOGO_URL", "/")
#: Any valid value for CSS with to control the width of the logo image
LOGO_WIDTH: str = app_settings.get("LOGO_WIDTH", "100%")
#: The name of the site to use in the title of the page.
SITE_NAME: str = app_settings.get("SITE_NAME", "Sphinx Hosting")
#: The maximum nesting depth for the generated global table of contents.
MAX_GLOBAL_TOC_TREE_DEPTH: int = app_settings.get("MAX_GLOBAL_TOC_TREE_DEPTH", 2)
#: Version glob patterns that if matched, will exlude the version from being
#: marked as latest.  This is primarily for .dev. versions.j
EXCLUDE_FROM_LATEST: list[str] = app_settings.get(
    "EXCLUDE_FROM_LATEST", ["*-dev*", "*-alpha*", "*-beta*", "*-rc*"]
)
#: Additional static menu items configured for the main navigation.
EXTRA_MENU_ITEMS: list[dict[str, Any]] = app_settings.get(
    EXTRA_MENU_ITEMS_SETTING, []
)
