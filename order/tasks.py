# Copyright 2004-present, Facebook. All Rights Reserved.
from celery import shared_task
from celery.utils.log import get_task_logger
from catalog.utils import post_item_batch_by_id
from .utils import (
    fetch_and_ack_orders_by_id,
    cancel_order_by_id,
    refund_order_by_id,
    fulfill_order_by_id,
    get_order_items,
)
logger = get_task_logger(__name__)


@shared_task
def fetch_orders_async(store_id):
    ''' Async task to fetch and ack orders for store_id '''
    logger.info("fetch_orders_async for store id {}".format(store_id))
    fetched_orders, acked_orders = fetch_and_ack_orders_by_id(store_id)


@shared_task
def fulfill_order_async(order_id, carrier, tracking_number, items=None):
    ''' Async task to fulfill an order by id, and sync the order's items

    params:
    order_id: id of the Order to fulfill
    carrier: the shipping carrier
    tracking_number: tracking number from the carrier
    items: the subset of items this particular fulfillment is for
    '''
    logger.info("fulfill_order_async for order id {}".format(order_id))
    order, _ = fulfill_order_by_id(order_id, carrier, tracking_number, items)

    # check if fulfill is successful
    if order is not None:
        # get just items in the order or items being fulfilld for syncing
        items = items or get_order_items(order)
        logger.info("sync catalog to FB after fulfill order for store id {}{}".format(
                order.store.id,
                ", and products: {}".format(items) if items else "."
            )
        )
        res = post_item_batch_by_id(order.store.id, True, items)
        logger.info("post_item_batch_by_id response: {}".format(res.json()))


@shared_task
def cancel_order_async(order_id, cancel_reason, restock_items:bool = False, items=None):
    ''' Async task to cancel an order by order id

    params:
    order_id: order_id of order to cancel
    cancel_reason: CancellationReasonCode
    restock_items: set True if inventory should be restocked on successful cancel
    items: the subset of items this particular cancellation is for
    '''
    logger.info("cancel_order_async for order id {}".format(order_id))
    cancel_order_by_id(order_id, cancel_reason, restock_items, items)

@shared_task
def refund_order_async(order_id, reason_code, items=None):
    ''' Async task to refund an order by order id

    params:
    order_id: order_id of the Order to refund
    reason_code: refund reason code
    items: the subset of items this particular refund is for
    '''
    logger.info("refund_order_async for order id {}".format(order_id))
    refund_order_by_id(order_id, reason_code, items)
