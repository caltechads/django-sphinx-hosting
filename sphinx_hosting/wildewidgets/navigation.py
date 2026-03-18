from __future__ import annotations

from collections.abc import Iterable
from copy import deepcopy
from functools import lru_cache
from typing import TYPE_CHECKING, Any, ClassVar, Final, Protocol, TypeAlias, cast

from crequest.middleware import CrequestMiddleware
from django.conf import settings
from django.urls import reverse_lazy
from django.utils.module_loading import import_string
from wildewidgets import (
    Block,
    BreadcrumbBlock,
    BreadcrumbItem,
    LinkedImage,
    Menu,
    MenuItem,
    TablerVerticalNavbar,
)

from ..settings import (
    EXTRA_MENU_ITEMS_SETTING,
    LOGO_IMAGE,
    LOGO_URL,
    LOGO_WIDTH,
    MENU_ITEM_BUILDERS_SETTING,
    SITE_NAME,
)
from .search import GlobalSearchFormWidget

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser
    from django.http.request import HttpRequest

#: Allowed keys for ``SPHINX_HOSTING_SETTINGS["EXTRA_MENU_ITEMS"]`` item dicts.
ALLOWED_MENU_ITEM_KEYS: Final[frozenset[str]] = frozenset(
    {"active", "icon", "items", "text", "url"}
)

#: The setting path used in validation error messages for extra menu items.
EXTRA_MENU_ITEMS_SOURCE: Final[str] = "SPHINX_HOSTING_SETTINGS['EXTRA_MENU_ITEMS']"
#: The setting path used in validation error messages for menu builders.
MENU_ITEM_BUILDERS_SOURCE: Final[str] = (
    "SPHINX_HOSTING_SETTINGS['MENU_ITEM_BUILDERS']"
)

#: A dictionary menu item spec accepted from settings and hook builders.
MenuItemDict: TypeAlias = dict[str, Any]
#: The supported menu item spec shape.
MenuItemSpec: TypeAlias = MenuItem | MenuItemDict
#: The supported return shape from a configured menu item builder.
MenuBuilderResult: TypeAlias = MenuItemSpec | Iterable[MenuItemSpec] | None


class MenuItemBuilder(Protocol):
    """
    Protocol for a conditional menu-item builder callable.

    The callable may return ``None``, one item, or an iterable of items.
    """

    def __call__(
        self,
        *,
        request: HttpRequest,
        user: AbstractUser,
        menu: SphinxHostingMainMenu,
    ) -> MenuBuilderResult:
        """
        Build conditional menu items for one request/user.

        Keyword Args:
            request: The current Django request.
            user: The authenticated user for this request.
            menu: The active menu instance being built.

        Returns:
            One or more menu item specs, or ``None``.

        """


def _get_app_setting(name: str, default: Any) -> Any:
    """
    Read one value from ``SPHINX_HOSTING_SETTINGS``.

    Args:
        name: The key to read from ``SPHINX_HOSTING_SETTINGS``.
        default: The fallback value when the key is missing.

    Returns:
        The setting value or the fallback default.

    """
    return getattr(settings, "SPHINX_HOSTING_SETTINGS", {}).get(name, default)


@lru_cache(maxsize=64)
def _resolve_menu_item_builders(paths: tuple[str, ...]) -> tuple[MenuItemBuilder, ...]:
    """
    Resolve dotted import paths to callable builder objects.

    Args:
        paths: Dotted import paths for menu item builder callables.

    Returns:
        A tuple of resolved builder callables.

    Raises:
        TypeError: One or more resolved objects is not callable.

    """
    builders: list[MenuItemBuilder] = []
    for path in paths:
        builder = import_string(path)
        if not callable(builder):
            msg = (
                f"{MENU_ITEM_BUILDERS_SOURCE} path '{path}' resolved to "
                f"'{type(builder).__name__}', which is not callable."
            )
            raise TypeError(msg)
        builders.append(cast("MenuItemBuilder", builder))
    return tuple(builders)


def get_menu_item_builders() -> tuple[MenuItemBuilder, ...]:
    """
    Return configured conditional menu-item builders.

    Returns:
        A tuple of resolved builder callables.

    Raises:
        TypeError: ``MENU_ITEM_BUILDERS`` is not a list of dotted-path strings.

    """
    raw_paths = _get_app_setting(MENU_ITEM_BUILDERS_SETTING, [])
    if raw_paths is None:
        return ()
    if not isinstance(raw_paths, list):
        msg = f"{MENU_ITEM_BUILDERS_SOURCE} must be a list of dotted-path strings."
        raise TypeError(msg)
    for index, path in enumerate(raw_paths):
        if not isinstance(path, str):
            msg = (
                f"{MENU_ITEM_BUILDERS_SOURCE}[{index}] must be a dotted-path string, "
                f"got '{type(path).__name__}'."
            )
            raise TypeError(msg)
    return _resolve_menu_item_builders(tuple(raw_paths))


def _normalize_menu_item(item: MenuItemSpec, *, source: str) -> MenuItem:
    """
    Normalize one menu item spec into a :py:class:`wildewidgets.MenuItem`.

    Args:
        item: A ``MenuItem`` object or dictionary menu item specification.

    Keyword Args:
        source: Human-readable source path for validation errors.

    Returns:
        A normalized ``MenuItem``.

    Raises:
        TypeError: The item uses an invalid type.
        ValueError: The item schema includes unknown or missing keys.

    """
    if isinstance(item, MenuItem):
        return deepcopy(item)
    if not isinstance(item, dict):
        msg = f"{source} must be a MenuItem or dict, got '{type(item).__name__}'."
        raise TypeError(msg)

    unknown = sorted(set(item) - ALLOWED_MENU_ITEM_KEYS)
    if unknown:
        msg = f"{source} contains unknown keys: {', '.join(unknown)}."
        raise ValueError(msg)

    if "text" not in item:
        msg = f"{source} must define required key 'text'."
        raise ValueError(msg)

    text = item["text"]
    if not isinstance(text, str):
        msg = f"{source}['text'] must be a string."
        raise TypeError(msg)

    url = item.get("url")
    if url is not None and not isinstance(url, str):
        msg = f"{source}['url'] must be a string when provided."
        raise TypeError(msg)

    icon = item.get("icon")
    if icon is not None and not isinstance(icon, (str, Block)):
        msg = f"{source}['icon'] must be a string or Block when provided."
        raise TypeError(msg)

    active = item.get("active", False)
    if not isinstance(active, bool):
        msg = f"{source}['active'] must be a bool when provided."
        raise TypeError(msg)

    child_items = item.get("items", [])
    if child_items is None:
        child_items = []
    if not isinstance(child_items, list):
        msg = f"{source}['items'] must be a list when provided."
        raise TypeError(msg)
    children = _normalize_menu_items(child_items, source=f"{source}['items']")
    return MenuItem(text=text, icon=icon, url=url, active=active, items=children)


def _normalize_menu_items(
    items: Iterable[MenuItemSpec], *, source: str
) -> list[MenuItem]:
    """
    Normalize a collection of menu item specs.

    Args:
        items: The menu item specs to normalize.

    Keyword Args:
        source: Human-readable source path for validation errors.

    Returns:
        A list of normalized ``MenuItem`` objects.

    Raises:
        TypeError: One or more items use an invalid type.
        ValueError: One or more items have an invalid schema.

    """
    normalized: list[MenuItem] = []
    for index, item in enumerate(items):
        normalized.append(_normalize_menu_item(item, source=f"{source}[{index}]"))
    return normalized


def _normalize_builder_result(
    result: MenuBuilderResult, *, source: str
) -> list[MenuItem]:
    """
    Normalize a builder return value into menu items.

    Args:
        result: The raw builder return value.

    Keyword Args:
        source: Human-readable source path for validation errors.

    Returns:
        A list of normalized ``MenuItem`` objects.

    Raises:
        TypeError: The return type is invalid.
        ValueError: One or more returned item specs have invalid schema.

    """
    if result is None:
        return []
    if isinstance(result, (MenuItem, dict)):
        return [_normalize_menu_item(result, source=source)]
    if isinstance(result, (str, bytes)) or not isinstance(result, Iterable):
        msg = (
            f"{source} must return None, a menu item spec, or an iterable of "
            "menu item specs."
        )
        raise TypeError(msg)
    return _normalize_menu_items(result, source=source)


class SphinxHostingMainMenu(Menu):
    """
    The primary menu that appears in :py:class:`SphinxHostingSidebar`.

    It appears directly underneath
    :py:class:`sphinx_hosting.wildewidgets.search.GlobalSearchFormWidget`.
    The menu always includes the Project index and may include conditional
    items based on user permissions and project-level hook builders.

    Args:
        items: Additional menu items to inject at construction time.

    Keyword Args:
        kwargs: Keyword arguments forwarded to :py:class:`wildewidgets.Menu`.

    """

    title: str = "Main"
    items: Final[list[MenuItem]] = [
        MenuItem(
            text="Projects",
            icon="stack",
            url=reverse_lazy("sphinx_hosting:project--list"),
        )
    ]

    def __init__(self, *items, **kwargs) -> None:
        #: The active item in the menu.
        self.active_item: str | None = None
        super().__init__(*items, **kwargs)

    def _get_request(self) -> HttpRequest:
        """
        Return the current request from ``django-crequest`` middleware.

        Returns:
            The current Django request.

        Raises:
            RuntimeError: The current request is unavailable.

        """
        request = CrequestMiddleware.get_request()
        if request is None:
            msg = (
                "SphinxHostingMainMenu requires an active request from "
                "CrequestMiddleware, but none was available."
            )
            raise RuntimeError(msg)
        return cast("HttpRequest", request)

    def _get_static_items(self, items: list[MenuItem]) -> list[MenuItem]:
        """
        Build deterministic static menu items for this request.

        Args:
            items: The base menu item list supplied by ``wildewidgets.Menu``.

        Returns:
            Base menu items followed by normalized ``EXTRA_MENU_ITEMS``.

        Raises:
            TypeError: ``EXTRA_MENU_ITEMS`` is not a list.
            ValueError: One or more item specs are invalid.

        """
        configured_items = _get_app_setting(EXTRA_MENU_ITEMS_SETTING, [])
        if not isinstance(configured_items, list):
            msg = f"{EXTRA_MENU_ITEMS_SOURCE} must be a list."
            raise TypeError(msg)
        static_items = [deepcopy(item) for item in items]
        static_items.extend(
            _normalize_menu_items(configured_items, source=EXTRA_MENU_ITEMS_SOURCE)
        )
        return static_items

    def _get_builtin_conditional_items(self, user: AbstractUser) -> list[MenuItem]:
        """
        Build conditional items provided by ``django-sphinx-hosting`` itself.

        Args:
            user: The user associated with the current request.

        Returns:
            A list of built-in conditional menu items.

        """
        conditional_items: list[MenuItem] = []
        if user.has_perm("sphinxhostingcore.view_classifier"):
            conditional_items.append(
                MenuItem(
                    text="Classifiers",
                    icon="sliders",
                    url=reverse_lazy("sphinx_hosting:classifier--index"),
                )
            )
        return conditional_items

    def _get_builder_conditional_items(
        self, request: HttpRequest, user: AbstractUser
    ) -> list[MenuItem]:
        """
        Build conditional items from configured menu builder callables.

        Args:
            request: The current request.
            user: The user associated with the current request.

        Returns:
            A list of normalized conditional menu items.

        Raises:
            TypeError: One or more builders return invalid item shapes.
            ValueError: One or more returned item specs are invalid.
            Exception: Any exception raised by a configured builder callable.

        """
        conditional_items: list[MenuItem] = []
        for index, builder in enumerate(get_menu_item_builders()):
            result = builder(request=request, user=user, menu=self)
            conditional_items.extend(
                _normalize_builder_result(
                    result, source=f"{MENU_ITEM_BUILDERS_SOURCE}[{index}]"
                )
            )
        return conditional_items

    def _set_active_item(self, items: list[MenuItem]) -> None:
        """
        Mark the active item across all menu entries.

        Args:
            items: Menu items to mark active.

        Side Effects:
            Mutates ``items`` active state in place.

        """
        if self.active_item is None:
            return
        for item in items:
            item.set_active(self.active_item)

    def build_menu(self, items: Iterable[MenuItem]) -> None:
        """
        Programmatically build the menu based on request-time context.

        We defer conditional and hook-driven menu construction until this method
        because URL resolution and request context are guaranteed here.

        Args:
            items: Base menu items from :py:class:`wildewidgets.Menu`.

        Raises:
            RuntimeError: Request context is unavailable.
            TypeError: A configured setting or builder return type is invalid.
            ValueError: A configured item spec is invalid.
            Exception: Any exception raised by configured menu builders.

        """
        request = self._get_request()
        user = cast("AbstractUser", request.user)
        menu_items = self._get_static_items(list(items))
        menu_items.extend(self._get_builtin_conditional_items(user))
        menu_items.extend(self._get_builder_conditional_items(request, user))
        self._set_active_item(menu_items)
        super().build_menu(menu_items)

    def activate(self, text: str) -> bool:
        """
        Save active-item text for deferred matching during :py:meth:`build_menu`.

        Args:
            text: The text or URL to search among menu items.

        Returns:
            ``True`` always, because matching is deferred to ``build_menu``.

        """
        self.active_item = text
        return True


class SphinxHostingSidebar(TablerVerticalNavbar):
    """
    The vertical menu area on the left of the page.

    It houses our search form,
    :py:class:`sphinx_hosting.wildewidgets.search.GlobalSearchFormWidget`, our
    main menu :py:class:`SphinxHostingMainMenu`, and the global table of
    contents menu when reading a specific documentation version.
    """

    hide_below_viewport: str = "xl"
    branding: Block = Block(
        LinkedImage(
            image_src=LOGO_IMAGE,
            image_width=LOGO_WIDTH,
            image_alt=SITE_NAME,
            css_class="d-flex justify-content-center",
            url=LOGO_URL,
        ),
        GlobalSearchFormWidget(css_class="ms-auto ms-xl-0 align-self-center mt-3"),
        css_class=(
            "d-flex flex-row flex-xl-column justify-content-between "
            "flex-grow-1 flex-xl-grow-0"
        ),
    )
    contents: Final[list[Block]] = [
        SphinxHostingMainMenu(),
    ]
    wide: bool = True


class SphinxHostingBreadcrumbs(BreadcrumbBlock):
    """
    The breadcrumbs that appear at the top of each page.
    """

    items: ClassVar[list[BreadcrumbItem]] = [
        BreadcrumbItem(
            title=SITE_NAME, url=reverse_lazy("sphinx_hosting:project--list")
        )
    ]
