# Copyright 2004-present, Facebook. All Rights Reserved.
from django.contrib import admin
from .models import WebhookNotification

admin.site.register(WebhookNotification)
