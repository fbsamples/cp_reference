# Copyright 2004-present, Facebook. All Rights Reserved.
#!/usr/bin/env python3

# @lint-ignore FBCODEBUCKFORMAT
from .base import * # noqa: F403, F401
import os
import dj_database_url

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

heroku_app_domain = os.getenv('ALLOWED_PRODUCTION_HEROKU_HOST')

ALLOWED_HOSTS = [
    heroku_app_domain,
    "127.0.0.1",
]

DATABASES = {
    "default": dj_database_url.config(default=os.getenv('DATABASE_URL'))
}
