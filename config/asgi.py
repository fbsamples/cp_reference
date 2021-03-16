# Copyright 2004-present, Facebook. All Rights Reserved.
#!/usr/bin/env python3

"""
ASGI config for cp_reference project.
It exposes the ASGI callable as a module-level variable named ``application``.
For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.setttings.development",
)

application = get_asgi_application()
