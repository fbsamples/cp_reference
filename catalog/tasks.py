# Copyright 2004-present, Facebook. All Rights Reserved.
from celery import shared_task
from celery.utils.log import get_task_logger
from catalog.utils import post_item_batch_by_id

logger = get_task_logger(__name__)

@shared_task
def sync_catalog_async(store_id, allow_upsert=True, items=None):
    ''' async task to sync catalog to FB

    params:
    store_id: store whose catalog is to be sync's
    allow_upsert: if True, items in the batch request not in the FB catalog will be created.
    items: specific set of items to sync
    '''

    logger.info("sync_catalog_async for store id {}{}".format(
            store_id,
            ", and products: {}".format(items) if items else "."
        )
    )
    res = post_item_batch_by_id(store_id, allow_upsert, items)
    logger.info("post_item_batch_by_id response: {}".format(res.json()))
