# Copyright 2004-present, Facebook. All Rights Reserved.
# Create your tasks here

from celery import shared_task
from celery.utils.log import get_task_logger
from order.tasks import fetch_orders_async
from catalog.tasks import sync_catalog_async
from shop.models import Store

logger = get_task_logger(__name__)

@shared_task
def periodic_orders_sync_all_stores():
    ''' Scheduled task to sync orders for all stores '''
    logger.info("periodic_orders_sync_all_stores")
    stores = Store.objects.all()
    # to avoid overloading redis
    # try distributing fetch for stores over few seconds
    # also set an expiration of 5 min
    for index, store in enumerate(stores, start=1):
        fetch_orders_async.apply_async(kwargs={
            "store_id": store.id
        }, countdown = index + 2, expires = 5 * 60)

@shared_task
def periodic_catalog_sync_all_stores():
    ''' Scheduled task to sync catalog for all stores '''
    logger.info("periodic_catalog_sync_all_stores")
    stores = Store.objects.all()
    for index, store in enumerate(stores, start=1):
        sync_catalog_async.apply_async(kwargs={
            "store_id": store.id
        }, countdown = index + 3, expires = 5 * 60)
