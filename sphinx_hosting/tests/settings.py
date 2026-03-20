from typing import Any, cast

from demo.settings import *  # noqa: F403

HAYSTACK_CONNECTIONS = {
    "default": {
        "ENGINE": "haystack.backends.simple_backend.SimpleEngine",
    }
}

DATABASES = cast("dict[str, dict[str, Any]]", globals()["DATABASES"])
DATABASES["default"] = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": ":memory:",
}
