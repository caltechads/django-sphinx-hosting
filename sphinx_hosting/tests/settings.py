from demo.settings import *  # noqa: F403

HAYSTACK_CONNECTIONS = {
    "default": {
        "ENGINE": "haystack.backends.simple_backend.SimpleEngine",
    }
}

DATABASES["default"]["NAME"] = str(DATABASES["default"]["NAME"])  # noqa: F405
