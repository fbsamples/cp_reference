# Copyright 2004-present, Facebook. All Rights Reserved.
import json
from datetime import datetime, timezone

from fb_metadata.models.fb_metadata import FacebookMetadata
from .models import WebhookNotification
from .choices import WebhookEvents


def processWebhookNotification(raw_data):
    ''' process the raw data provided by a webhook notification

    params:
    raw_data: raw data in json format from webhook
    '''
    # currently only processing setup statuses of commerce accounts
    raw_data = json.loads(raw_data)
    topic = raw_data["object"]
    entry = raw_data['entry'][0]
    time_sent = entry['time']
    commerce_account_id = entry['id']
    change = entry['changes'][0]
    event = change['field']
    value = change['value'] # noqa: F841

    # save notification
    fb_metadata = FacebookMetadata.objects.filter(commerce_account_id__exact=commerce_account_id).first()
    store = fb_metadata.store
    new_notification = WebhookNotification(
        store=store,
        topic=topic,
        event=event,
        time_sent=datetime.fromtimestamp(time_sent, timezone.utc),
        raw_notification_data=json.dumps(raw_data)
    )
    new_notification.save()

    if event == WebhookEvents.SETUP_STATUS:
        fb_metadata.fb_shop_setup_status = value.get('shop_setup', '')
        fb_metadata.fb_shop_payment_setup_status = value.get('payment_setup', '')
        fb_metadata.fb_shop_review_status = value.get('review_status', {}).get('status','')
        fb_metadata.save()
