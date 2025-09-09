from .base import *  # noqa


DEBUG = True

# Enable Django Debug Toolbar only in local
INSTALLED_APPS = INSTALLED_APPS + ["debug_toolbar"]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
] + MIDDLEWARE

INTERNAL_IPS = ["127.0.0.1", "localhost"]

# Workaround: Avoid PostgreSQL rejecting 'UTC' by not forcing DB timezone
USE_TZ = False


