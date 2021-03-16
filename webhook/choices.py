# Copyright 2004-present, Facebook. All Rights Reserved.
from django.db import models
from django.utils.translation import gettext_lazy

class WebhookTopics(models.TextChoices):
    ''' webhook Topics matching specific subsections of webhook notification data '''
    # currently we only handle COMMERCE_ACCOUNT related notifications like BI review success
    COMMERCE_ACCOUNT = "COMMERCE_ACCOUNT", gettext_lazy("commerce account")

class WebhookEvents(models.TextChoices):
    ''' Webhook Event types matching sepcific subsections of webhook notification data '''
    # currently we only handle shop setup statuses
    SETUP_STATUS = "setup_status", gettext_lazy("setup status")
