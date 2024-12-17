import logging
import logging.config
from typing import Any, Dict, List, Optional, Tuple  # noqa: UP035

import environ
import structlog

from . import __version__
from .logging import censor_password_processor, request_context_logging_processor

# The name of our project
# ------------------------------------------------------------------------------
PROJECT_NAME: str = "demo"
HUMAN_PROJECT_NAME: str = "Sphinx Hosting Demo"

# Load our environment with django-environ
BASE_DIR: environ.Path = environ.Path(__file__) - 2
APPS_DIR: environ.Path = BASE_DIR.path(PROJECT_NAME)

env: environ.Env = environ.Env()

# ==============================================================================

# DEBUG is Django's own config variable, while DEVELOPMENT is ours.
# Use DEVELOPMENT for things that you want to be able to enable/disable in dev
# without altering DEBUG, since that affects lots of other things.
DEBUG: bool = env.bool("DEBUG", default=False)
DEVELOPMENT: bool = env.bool("DEVELOPMENT", default=False)
TESTING: bool = env.bool("TESTING", default=False)
# Set BOOTSTRAP_ALWAYS_MIGRATE to True if you want to always run pending
# migrations on container boot up
BOOTSTRAP_ALWAYS_MIGRATE: bool = env.bool("BOOTSTRAP_ALWAYS_MIGRATE", default=True)

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/3.2/ref/settings/#secret-key
# You MUST define a unique DJANGO_SECRET_KEY env var for your app. And be sure
# not to use $ or # in the value.  The default is there for tests ONLY.
SECRET_KEY: str = env(
    "DJANGO_SECRET_KEY",
    default="Z4peQSPAoo8fruA7pRXt2LefJD2lqYvXtgPFxF2hAeUd7NGOpA8fAt3UpnXpJ019",
)
# https://docs.djangoproject.com/en/3.2/ref/settings/#allowed-hosts
ALLOWED_HOSTS: List[str] = env.list("DJANGO_ALLOWED_HOSTS", default=["*"])

# INTERNATIONALIZATION (i18n) AND LOCALIZATION (l10n)
# Change these values to suit this project.
# https://docs.djangoproject.com/en/3.2/topics/i18n/
# ------------------------------------------------------------------------------
LANGUAGE_CODE: str = "en-us"
TIME_ZONE: str = "America/Los_Angeles"
USE_I18N: bool = False
USE_L10N: bool = False
USE_TZ: bool = True

# DATABASES
# -----------
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
if TESTING:
    DATABASES: Dict[str, Dict[str, Any]] = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR.path("db.sqlite3"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": env("DB_NAME", default="demo"),
            "USER": env("DB_USER", default="demo_u"),
            "PASSWORD": env("DB_PASSWORD", default="password"),
            "HOST": env("DB_HOST", default="db"),
            "ATOMIC_REQUESTS": True,
            # This is needed in case the database doesn't have the newer default
            # settings that enable "strict mode".
            "OPTIONS": {
                "sql_mode": "traditional",
            },
        }
    }
DEFAULT_AUTO_FIELD: str = "django.db.models.AutoField"

# CACHES
# ------------------------------------------------------------------------------
# Disable all caching if the optional DISABLE_CACHE env var is True.
if env.bool("DISABLE_CACHE", default=False):
    CACHES: Dict[str, Any] = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }

# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/3.2/ref/settings/#root-urlconf
# noinspection PyUnresolvedReferences
ROOT_URLCONF: str = f"{PROJECT_NAME}.urls"
# https://docs.djangoproject.com/en/3.2/ref/settings/#wsgi-application
WSGI_APPLICATION: str = f"{PROJECT_NAME}.wsgi.application"

# APPS
# ------------------------------------------------------------------------------
DJANGO_APPS: List[str] = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 'django.contrib.humanize', # Handy template tags
    "django.contrib.admin",
]
THIRD_PARTY_APPS: List[str] = [
    "django_extensions",
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "drf_spectacular",
    "sass_processor",
    "crispy_forms",
    "crispy_bootstrap5",
    "haystack",
    "academy_theme",
    "wildewidgets",
    "sphinx_hosting",
    "sphinx_hosting.api",
]
LOCAL_APPS: List[str] = [
    "demo.users",
    "demo.core",
]
# https://docs.djangoproject.com/en/3.2/ref/settings/#installed-apps
INSTALLED_APPS: List[str] = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# AUTHENTICATION
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/3.2/ref/settings/#authentication-backends
AUTHENTICATION_BACKENDS: List[str] = [
    "django.contrib.auth.backends.ModelBackend",
]

# Use our custom User model instead of auth.User, because it's good practice to
# define a custom one at the START.
AUTH_USER_MODEL: str = "users.User"

# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS: List[Dict[str, str]] = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"  # noqa: E501
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# MIDDLEWARE
# ------------------------------------------------------------------------
MIDDLEWARE: List[str] = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "xff.middleware.XForwardedForMiddleware",
    "crequest.middleware.CrequestMiddleware",
]

# STATIC
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/3.2/ref/settings/#static-root
# noinspection PyUnresolvedReferences
STATIC_ROOT: str = "/static"
# https://docs.djangoproject.com/en/3.2/ref/settings/#static-url
STATIC_URL: str = "/static/"
# https://docs.djangoproject.com/en/3.2/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS: List[str] = []
# https://docs.djangoproject.com/en/3.2/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS: List[str] = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "sass_processor.finders.CssFinder",
]

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-file-storage
DEFAULT_FILE_STORAGE: str = "django.core.files.storage.FileSystemStorage"
# https://docs.djangoproject.com/en/3.2/ref/settings/#media-root
# noinspection PyUnresolvedReferences
MEDIA_ROOT: str = "/media"
# https://docs.djangoproject.com/en/3.2/ref/settings/#media-url
MEDIA_URL: str = "/media/"

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/3.2/ref/settings/#templates
TEMPLATES: List[Dict[str, Any]] = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "OPTIONS": {
            # https://docs.djangoproject.com/en/3.2/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/3.2/ref/templates/api/#loader-types
            # Always use Django's cached templates loader, even in dev with
            # DEBUG==True.  We use RequestLevelTemplateCacheMiddleware in dev to
            # clear that cache at the start of each request, so that the latest
            # template changes get loaded without having to reboot gunicorn.
            "loaders": [
                (
                    "django.template.loaders.cached.Loader",
                    [
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ],
                ),
            ],
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "academy_theme.context_processors.theme",
            ],
        },
    },
]

# FIXTURES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/3.2/ref/settings/#fixture-dirs
FIXTURE_DIRS: Tuple[str, ...] = (str(APPS_DIR.path("fixtures")),)

# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/3.2/ref/settings/#secure-proxy-ssl-header
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # noqa: ERA001
# https://docs.djangoproject.com/en/3.2/ref/settings/#secure-ssl-redirect
# SECURE_SSL_REDIRECT = env.bool('DJANGO_SECURE_SSL_REDIRECT', default=True)  # noqa: E501, ERA001
# https://docs.djangoproject.com/en/3.2/ref/settings/#session-cookie-httponly
SESSION_COOKIE_HTTPONLY: bool = True
# https://docs.djangoproject.com/en/3.2/ref/settings/#session-cookie-secure
SESSION_COOKIE_SECURE: bool = True
# https://docs.djangoproject.com/en/2.0/ref/settings/#session-cookie-name
SESSION_COOKIE_NAME: str = f"{PROJECT_NAME}_session"
# https://docs.djangoproject.com/en/3.2/ref/settings/#csrf-cookie-httponly
CSRF_COOKIE_HTTPONLY: bool = True
# https://docs.djangoproject.com/en/2.0/ref/settings/#csrf-cookie-name
CSRF_COOKIE_NAME: str = f"{PROJECT_NAME}_csrftoken"
# https://docs.djangoproject.com/en/3.0/ref/settings/#csrf-cookie-secure
CSRF_COOKIE_SECURE: bool = True
# https://docs.djangoproject.com/en/3.2/ref/settings/#csrf-trusted-origins
CSRF_TRUSTED_ORIGINS: List[str] = []
# https://docs.djangoproject.com/en/3.2/ref/settings/#secure-browser-xss-filter
SECURE_BROWSER_XSS_FILTER: bool = True
# https://docs.djangoproject.com/en/3.2/ref/settings/#x-frame-options
X_FRAME_OPTIONS: str = "DENY"
# https://docs.djangoproject.com/en/3.2/ref/settings/#session-expire-at-browser-close
# Don't use persistent sessions, since that could lead to a sensitive information leak.
SESSION_EXPIRE_AT_BROWSER_CLOSE: bool = True
# https://docs.djangoproject.com/en/3.2/ref/settings/#session-cookie-age
if not DEBUG:
    # Chrome and Firefox ignore SESSION_EXPIPE_AT_BROWSER_CLOSE
    SESSION_COOKIE_AGE: int = 60 * 120

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-from-email
DEFAULT_FROM_EMAIL: str = env(
    "DJANGO_DEFAULT_FROM_EMAIL", default=f"{HUMAN_PROJECT_NAME} <noreply@example.com>"
)
# https://docs.djangoproject.com/en/3.2/ref/settings/#server-email
SERVER_EMAIL: str = env("DJANGO_SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)
# https://docs.djangoproject.com/en/3.2/ref/settings/#email-subject-prefix
EMAIL_SUBJECT_PREFIX: str = env(
    "DJANGO_EMAIL_SUBJECT_PREFIX", default=f"[{HUMAN_PROJECT_NAME}]"
)
EMAIL_BACKEND: str = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST: str = env("EMAIL_HOST", default="mail")
EMAIL_HOST_USER: Optional[str] = env("EMAIL_HOST_USER", default=None)  # noqa: FA100
EMAIL_HOST_PASSWORD: Optional[str] = env("EMAIL_HOST_PASSWORD", default=None)  # noqa: FA100
EMAIL_USE_TLS: bool = env.bool("EMAIL_USE_TLS", default=False)
EMAIL_PORT: int = env.int("EMAIL_PORT", default=1025)

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL.
ADMIN_URL: str = env("DJANGO_ADMIN_URL", default="admin/")
# https://docs.djangoproject.com/en/3.2/ref/settings/#admins
ADMINS: List[Tuple[str, str]] = [
    ("Sphinx Hosting Demo Admins", "sphinx-hosting-demo@example.com")
]
# https://docs.djangoproject.com/en/3.2/ref/settings/#managers
MANAGERS = ADMINS

# LOGGING
# ------------------------------------------------------------------------------
# Use structlog to ease the difficulty of adding context to log messages
# See https://structlog.readthedocs.io/en/stable/index.html
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        request_context_logging_processor,
        censor_password_processor,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=False,
)

pre_chain = [
    structlog.processors.StackInfoRenderer(),
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.processors.TimeStamper(fmt="iso"),
]

# Build our custom logging config.
LOGGING_CONFIG: Optional[Dict[str, Any]] = None  # noqa: FA100
LOGGING: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {
        "handlers": ["structlog_console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["structlog_console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.security.DisallowedHost": {
            # We don't care about attempts to access the site with a spoofed
            # HTTP-HOST header. It clutters the logs.
            "handlers": ["null"],
            "propagate": False,
        },
        "qinspect": {
            # This is the QueryInspect logger. We always configure it (to
            # simplify the logging setup code), but it doesn't get used unless
            # we turn on QueryInspect.
            "handlers": ["structlog_console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
    "handlers": {
        "structlog_console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "structlog",
        },
        "null": {
            "level": "DEBUG",
            "class": "logging.NullHandler",
        },
    },
    "formatters": {
        # Set up a special formatter for our structlog output
        "structlog": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(repr_native_str=False),
            "foreign_pre_chain": pre_chain,
            # Prefix our logs with SYSLOG to make them easier to either grep in or out
            "format": "SYSLOG %(message)s",
        },
    },
}
logging.config.dictConfig(LOGGING)

# django-haystack
# ------------------------------------------------------------------------------
HAYSTACK_CONNECTIONS: Dict[str, Any] = {
    "default": {
        "ENGINE": "haystack.backends.elasticsearch7_backend.Elasticsearch7SearchEngine",
        "URL": "http://search:9200/",
        "INDEX_NAME": "sphinx_hosting",
    },
}

# crispy-forms
# ------------------------------------------------------------------------------
CRISPY_ALLOWED_TEMPLATE_PACKS: str = "bootstrap5"
CRISPY_TEMPLATE_PACK: str = "bootstrap5"


# django-theme-academy
# ------------------------------------------------------------------------------
ACADEMY_THEME_SETTINGS: Dict[str, Any] = {
    # Header
    "APPLE_TOUCH_ICON": "core/images/apple-touch-icon.png",
    "FAVICON_32": "core/images/favicon-32x32.png",
    "FAVICON_16": "core/images/favicon-16x16.png",
    "FAVICON": "core/images/favicon.ico",
    "SITE_WEBMANIFEST": "core/images/site.webmanifest",
    # Footer
    "ORGANIZATION_LINK": "https://github.com/caltechads/django-sphinx-hosting",
    "ORGANIZATION_NAME": "Sphinx Hosting",
    "ORGANIZATION_ADDRESS": "123 Main Street, Everytown, ST",
    "COPYRIGHT_ORGANIZATION": "Sphinx Hosting",
    "FOOTER_LINKS": [],
}

# django-wildewidgets
# ------------------------------------------------------------------------------
WILDEWIDGETS_DATETIME_FORMAT: str = "%Y-%m-%d %H:%M %Z"

# django-xff
# ------------------------------------------------------------------------------
XFF_TRUSTED_PROXY_DEPTH: int = env.int("XFF_TRUSTED_PROXY_DEPTH", default=1)
XFF_HEADER_REQUIRED: bool = env.bool("XFF_HEADER_REQUIRED", default=False)

# Django REST Framework
# ------------------------------------------------------------------------------
# REST Framework
REST_FRAMEWORK: Dict[str, Any] = {
    # https://www.django-rest-framework.org/api-guide/throttling/
    "DEFAULT_THROTTLE_CLASSES": ("rest_framework.throttling.UserRateThrottle",),
    "DEFAULT_THROTTLE_RATES": {
        "user": "1000/day",
    },
    # https://www.django-rest-framework.org/api-guide/parsers/#setting-the-parsers
    "DEFAULT_PARSER_CLASSES": ("rest_framework.parsers.JSONParser",),
    # https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
    ),
    # https://django-filter.readthedocs.io/en/master/guide/rest_framework.html
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    # https://www.django-rest-framework.org/api-guide/pagination/#limitoffsetpagination
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    # https://github.com/tfranzel/drf-spectacular
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "PAGE_SIZE": 100,
}

# drf-spectacular
# ------------------------------------------------------------------------------
# https://drf-spectacular.readthedocs.io/en/latest/settings.html
SPECTACULAR_SETTINGS: Dict[str, Any] = {
    "SCHEMA_PATH_PREFIX": r"/api/v1",
    "SERVERS": [{"url": "https://localhost", "description": "Django Sphinx Hosting"}],
    "TITLE": "Django Sphinx Hosting",
    "VERSION": __version__,
    "DESCRIPTION": """


## Authentication

The Sphinx Hosting Demo API uses Token based authentication.   To use the API:

* You must have a Django user in the system
* That Django user must have an API Token associated with its User object

Then, on each `GET` to the API caller must supply an `Authorization` request header on each of your requests that looks
like so:

```
Authorization: Token b422b0e7d1d11f5060613c01c4ccd1b00174b876
```

replacing that hex string with your actual authoriztion token.  Note that the auth token should be preceeded with the
string literal "Token" with whitespace separating the two strings.

Here's a properly formatted `curl` line that will hit the `/api/v1/projects/` endpoint:

```
curl -X GET \\
    -H 'Accept: application/json; indent=4' \\
    -H 'Authorization: Token b422b0e7d1d11f5060613c01c4ccd1b00174b876' \\
    --insecure \\
    --verbose \\
    https://${SERVER}:${PORT}/api/v1/projects/
```

## Pagination of list results

All list results are paginated, with the default page size of 100 items.   We paginate because a some of the queries are
very costly,  especially if you're getting a list result of a model with lots of rows.

Your results will all look something like this:

```
GET /api/v1/projects/
```

```json
{
    "count": 123,
    "next":"https://localhost/api/v1/projects/?limit=100&offset=100",
    "previous": null,
    "results": [
        [ ... ]
    ]
}
```

* To get to the next page of your results, `GET` the URL from the `next` key from the result dict
* To get the previous page, `GET` URL from the `prev` key from the result dict.

To get a different number of results per page, use the `limit` param:

```
GET /api/v1/projects/?limit=50
```

will retrieve 50 projects instead of 100.
""",  # noqa: E501
}


# django-debug-toolbar
# ------------------------------------------------------------------------------
# We don't enable the debug toolbar unless DEVELOPMENT is also True.
ENABLE_DEBUG_TOOLBAR = DEVELOPMENT and env.bool("ENABLE_DEBUG_TOOLBAR", default=False)
if ENABLE_DEBUG_TOOLBAR:
    # https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#prerequisites
    INSTALLED_APPS += ["debug_toolbar"]
    # https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#middleware
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
    DEBUG_TOOLBAR_PANELS = [
        "debug_toolbar.panels.versions.VersionsPanel",
        "debug_toolbar.panels.timer.TimerPanel",
        "debug_toolbar.panels.settings.SettingsPanel",
        "debug_toolbar.panels.headers.HeadersPanel",
        "debug_toolbar.panels.request.RequestPanel",
        "debug_toolbar.panels.sql.SQLPanel",
        "debug_toolbar.panels.staticfiles.StaticFilesPanel",
        "debug_toolbar.panels.templates.TemplatesPanel",
        "debug_toolbar.panels.cache.CachePanel",
        "debug_toolbar.panels.signals.SignalsPanel",
        "debug_toolbar.panels.logging.LoggingPanel",
        "debug_toolbar.panels.redirects.RedirectsPanel",
    ]
    # https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html#debug-toolbar-config
    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TEMPLATE_CONTEXT": True,
        "SHOW_TOOLBAR_CALLBACK": lambda: True,
    }

# django-queryinspect
# ------------------------------------------------------------------------------
if DEVELOPMENT and env.bool("ENABLE_QUERYINSPECT", default=False):
    # Configure django-queryinspect
    MIDDLEWARE += ["qinspect.middleware.QueryInspectMiddleware"]
    # Whether the Query Inspector should do anything (default: False)
    QUERY_INSPECT_ENABLED = True
    # Whether to log the stats via Django logging (default: True)
    QUERY_INSPECT_LOG_STATS = True
    # Whether to add stats headers (default: True)
    QUERY_INSPECT_HEADER_STATS = False
    # Whether to log duplicate queries (default: False)
    QUERY_INSPECT_LOG_QUERIES = True
    # Whether to log queries that are above an absolute limit (default: None - disabled)
    QUERY_INSPECT_ABSOLUTE_LIMIT = 100  # in milliseconds
    # Whether to log queries that are more than X standard deviations above the
    # mean query time (default: None)
    QUERY_INSPECT_STANDARD_DEVIATION_LIMIT = 2
    # Whether to include tracebacks in the logs (default: False)
    QUERY_INSPECT_LOG_TRACEBACKS = False
    # Uncomment this to filter traceback output to include only lines of our
    # app's first-party code.  I personally don't find this useful, because the
    # offending Python is sometimes actually somewhere in django core.
    # QUERY_INSPECT_TRACEBACK_ROOTS = ['/']  # noqa: ERA001

# TESTING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/3.0/ref/settings/#std:setting-TEST_RUNNER
if TESTING:
    DEBUG = False
    # Set the root logger to only display WARNING logs and above during tests.
    logging.getLogger("").setLevel(logging.WARNING)
