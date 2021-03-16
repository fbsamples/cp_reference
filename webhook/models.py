# Copyright 2004-present, Facebook. All Rights Reserved.
from django.db import models
from .choices import WebhookEvents, WebhookTopics
from django.utils.timezone import now

class WebhookNotification(models.Model):
    ''' Stores webhook notification data we've received in the local db
    fields:
    store: the target store of the webhok notification
    topic: the Topic of the notif.  Currencly just processing Commerce Account related events
    event: the Event of the notif.  Currenclty only processing shop status type events.
    time_sent: time Notif was sent by FB
    time_received: time local server has recevied the notif
    raw_notification_data: raw notif data for more processing at a later time.
    '''
    store = models.ForeignKey("shop.Store", null=True, on_delete=models.CASCADE)
    topic = models.CharField(
        max_length=30,
        choices=WebhookTopics.choices,
        default=WebhookTopics.COMMERCE_ACCOUNT,
    )
    event = models.CharField(
        max_length=50,
        choices=WebhookEvents.choices,
    )
    time_sent = models.DateTimeField(default=now, blank=True)
    time_received = models.DateTimeField(default=now, blank=True)
    raw_notification_data = models.TextField(null=True, blank=True)

    def __str__(self):
        return "Shop: [{}] Topic: [{}] Event[{}]".format(self.store, self.topic, self.event)
