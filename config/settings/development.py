# Copyright 2004-present, Facebook. All Rights Reserved.
#!/usr/bin/env python3

# @lint-ignore FBCODEBUCKFORMAT
from .base import * # noqa: F403, F401
import os

DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3", # noqa: F405
    }
}
GENERATE_PRODUCT_LINK = False
