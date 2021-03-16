# Copyright 2004-present, Facebook. All Rights Reserved.
import requests
import json
from typing import List, Dict
from django.db import transaction
from django.conf import settings

from core.utils import get_idempotency_key
from catalog.models import Product
from shop.models import Store
from fb_metadata.models import FacebookMetadata
from order.models.choices import OrderStatus, OrderFulfillmentState, OrderCancellationState, OrderRefundState, CancellationReasonCode
from order.models import Customer, Order, OrderItem


def paginate_order_items(order_items:Dict):
    ''' Iterate through all order item pages and return a list of all order items

    params:
    order_items: dict of order items for an order, with a page of `data` and paging info.
    return:
    results: complete list of order items for this order.
    '''
    items = order_items['data']
    paging = order_items['paging']
    results = []
    results += items
    while 'next' in paging:
        res = requests.get(paging['next'])
        res = res.json()
        items = res['data']
        paging = res['paging']
        results += items
    return results


def pageinate_orders(orders:List[Dict]):
    ''' Iterate through a page (list) of orders and fetch the order items of each
    replace the paginated `item` field in the order data with the complete list

    params:
    orders: list (page) of orders whose order items can also be paginated.
    return:
    results: list of all orders from all pages with their order items resolved.
    '''
    results = []
    for order in orders:
        items = paginate_order_items(order['items'])
        results.append(order.copy())
        results[-1]['items']=items
    return results


def process_list_order_response(orders_response_json:Dict):
    ''' Build list of orders and their order items from response of first commerce_orders request

    params:
    orders_response_json: json of the response of commerce_orders GET call
    returns:
    results: complete list of orders with their order items
    '''

    if 'data' not in orders_response_json or not orders_response_json['data']:
        print("process_list_order_response found no orders to process")
        print(orders_response_json)
        return []

    orders = orders_response_json['data']
    results = []
    results += pageinate_orders(orders)
    paging = 'paging' in orders_response_json and orders_response_json['paging']
    if paging:
        while 'next' in paging:
            res = requests.get(results['paging']['next'])
            res = res.json()
            orders = res['data']
            paging = res['paging']
            results += pageinate_orders(orders)
    return results


def list_orders(page_id, token, states:List = None, fields:List = None):
    ''' list orders (bulk)

    params:
    page_id: FB page id
    token: access token
    states: inclusive list of filters for order states. If provided, OVERRIDES the default of "FB_PROCESSING,CREATED,IN_PROGRESS,COMPLETED"
    fields: inclusive list of fields to return. If provided, ADDS to the default of "id,order_status,items,buyer_details"

    returns:
    order_data: list of orders with their order items
    '''
    url = settings.BASE_API_URL + page_id + '/commerce_orders'
    params = {'access_token': token}
    params['state'] = ','.join(states) if states else 'FB_PROCESSING,CREATED,IN_PROGRESS,COMPLETED'
    params['fields'] = ','.join(set(fields).union({'id','items','order_status','buyer_details','shipping_address'})) if fields else "id,order_status,items,buyer_details,shipping_address"
    res = requests.get(url, params=params)
    order_data = process_list_order_response(res.json())
    return order_data


def acknowledge_orders(page_id, token, orders:List[Dict]):
    ''' acknowledge orders (bulk)
    acknowledge orders in bulk in batches of at most 100 orders
    some orders may not return with a "IN_PROGRESS" or properly ack'd state
    in that event we currently remove those orders from the local db.

    params:
    page_id: FB page id
    token: acces token
    orders: list of order ids and ext order ids to acknowledge.
    '''
    if len(orders)>100:
        raise Exception("Too many orders to acknowledge. Limit is 100.")
    url = settings.BASE_API_URL + page_id + '/acknowledge_orders'
    data = {
        'access_token': token,
        'idempotency_key': get_idempotency_key(),
        'orders': json.dumps(orders)
    }
    res = requests.post(url, data=data)
    print('acknowledge_orders response:',res.json())
    orders = res.json()['orders']
    [update_order_state(order['id'], OrderStatus.CONFIRMED_ORDER) if "state" in order and order['state']=="IN_PROGRESS" else delete_order(order['id']) for order in orders]


@transaction.atomic
def update_order_state(order, order_status:OrderStatus):
    ''' update order state by id or Order

    params:
    order: Order object or order id
    order_status: new OrderStatus to apply
    '''
    if not isinstance(order, Order):
        order = Order.objects.get(ext_order_id=order)
    order.order_status = order_status
    order.save()


@transaction.atomic
def update_order_fulfillment_state(order, order_fulfillment_state:OrderFulfillmentState):
    ''' update order fulfillment state by id or Order and decrement inventory

    params:
    order: Order object or order id
    order_fulfillment_state: new OrderFulfillmentState to apply
    '''
    if not isinstance(order, Order):
        order = Order.objects.get(ext_order_id=order)
    order.order_fulfillment_state = order_fulfillment_state

    # For all OrderItems in order, need to decrement inventory
    orderItems = OrderItem.objects.filter(order=order)
    for item in orderItems:
        product = item.product
        product.inventory = product.inventory - item.quantity
        product.save()
    order.save()


@transaction.atomic
def update_order_cancel_state(order, order_cancellation_state:OrderCancellationState):
    ''' update order cancellation state by id or Order

    params:
    order: Order object or order id
    order_cancellation_state: new OrderCancellationState to apply
    '''
    if not isinstance(order, Order):
        order = Order.objects.get(ext_order_id=order)
    order.order_cancellation_state = order_cancellation_state
    order.save()


@transaction.atomic
def update_order_refund_state(order, order_refund_state:OrderRefundState):
    ''' update order refund state by id or Order

    params:
    order: Order object or order id
    order_refund_state: new OrderRefundState to apply
    '''
    if not isinstance(order, Order):
        order = Order.objects.get(ext_order_id=order)
    order.order_refund_state = order_refund_state
    order.save()


@transaction.atomic
def delete_order(order):
    ''' delete order by id or Order, including all OrderItem

    params:
    order: Order object or order id
    '''
    if not isinstance(order, Order):
        order = Order.objects.get(ext_order_id=order)
    OrderItem.objects.filter(order=order).delete()
    order.delete()


@transaction.atomic
def write_orders(store:Store, orders:List[Dict]):
    ''' write orders and order items.  create Customer object if customer info is new.
    populate orders with 'merchant_order_reference' for acknowledge step

    note: retailer_id is a REQUIRED field of the items
    params:
    store: the store the orders belongs to
    orders: list of orders
    '''
    for order in orders:
        buyer = order.pop('buyer_details')
        shipping_addr_str = json.dumps(order.pop('shipping_address'))
        try:
            customer = Customer.objects.get(store=store, full_name=buyer['name'], email=buyer['email'], addr=shipping_addr_str)
        except Exception:
            print("Buyer info not found in Customer table.  Creating Customer entry for {} ({})".format(buyer['name'], buyer['email']))
            customer = Customer(
                store=store,
                full_name=buyer['name'],
                email=buyer['email'],
                addr=shipping_addr_str,
            )
            customer.save()
        try:
            order_model = Order.objects.get(store=store, customer=customer, ext_order_id=order['id'])
            print("Order with ext order id {} already exists".format(order['id']))
            continue
        except Exception:
            print("Order not found or is new, writing...")
            order_model = Order(
                store=store,
                customer=customer,
                ext_order_id=order['id'],
            )
            if order['order_status']['state'] == "IN_PROGRESS":
                print("WARN: order is already IN_PROGRESS and missing from orders table.  Filling.")
                order_model.order_status = OrderStatus.IN_PROGRESS
            order_model.save()
        items = order.pop('items')
        try:
            items_products = [(item, Product.objects.get(id=item['retailer_id'])) for item in items]
        except Exception:
            # at least 1 product does not exist in db (anymore)
            order_model.missing_items = True
            order_model.save()
            print("WARN: order contains products that no longer exist")
            continue
        # update order with 'merchant_order_reference' for the acknowledge step
        order['merchant_order_reference'] = order_model.id
        for item, product in items_products:
            try:
                item_model = OrderItem.objects.get(order=order_model, product=product)
                print("item product id {} already on order with id {}".format(product.id, order_model.id))
            except Exception:
                item_model = OrderItem(
                    order=order_model,
                    product=product,
                    quantity=int(item['quantity']),
                )
                item_model.save()


def fetch_and_ack_orders_by_id(store_id):
    store = Store.objects.get(id=store_id)
    return fetch_and_ack_orders(store)


def fetch_and_ack_orders(store):
    ''' fetch orders, write orders, ack orders, update/delete orders, in that order.

    params:
    store: store to fetch and ack orders for
    '''

    # get page id and token
    fb_meta = FacebookMetadata.objects.filter(store=store).first()
    if fb_meta is None:
        print("store [{}] doesnot have metadata, aborting order sync".format(store.name))
        return None, None
    page_id = fb_meta.fbe_page_id
    token = fb_meta.token_info
    if token is None:
        print("store [{}] doesnot have token info, aborting order sync".format(store.name))
        return None, None
    # get and store orders that are CREATED (need acking) and IN_PROGRESS (acked)
    # this way we sync up with any orders we may have missed during acking
    data = list_orders(page_id, token, states=["CREATED", "IN_PROGRESS"])
    fetched_orders = data.copy()
    # write orders also updates data with merchant_order_reference = local order id.
    write_orders(store, data)

    # acknowledge orders
    # parse out just the ext id and local id of orders that needs acknowledging ("CREATED")
    orders_to_ack = [{'id':order['id'], 'merchant_order_reference':order['merchant_order_reference']} for order in data if order['order_status']['state'] == 'CREATED']
    print("orders to acknowledge:", len(orders_to_ack))
    acked_orders = []
    try:
        with transaction.atomic():
            # loop through data 100 at a time due to limit.
            while orders_to_ack:
                batch = orders_to_ack[-100:]
                acknowledge_orders(page_id, token, batch)
                # only update orders after acknowledge_orders is successful
                orders_to_ack[-100:] = []
                acked_orders += batch
    except Exception as e:
        # only if something went wrong in the try block.  "normal" failures,
        # like if only some orders were successfully acked, are not handled here
        [delete_order(order['id']) for order in orders_to_ack]
        raise e
    return fetched_orders, acked_orders


def fulfill_order_by_id(order_id, carrier, tracking_number, items=None):
    ''' Fulfil an order by id
    NOTE: currently only fulfills an order COMPLETELY

    params:
    order_id: id of the Order to fulfill
    carrier: the shipping carrier
    tracking_number: tracking number from the carrier
    items: the subset of items this particular fulfillment is for
    returns:
    order, data:  tuple of the order object and response data if successful.
    '''
    order = Order.objects.get(id=order_id)
    return fulfill_order(order, carrier, tracking_number, items)


def fulfill_order(order:Order, carrier, tracking_number, items=None):
    ''' Fulfil an order
    NOTE: currently only fulfills an order COMPLETELY

    params:
    order: the Order to fulfill
    carrier: the shipping carrier
    tracking_number: tracking number from the carrier
    items: the subset of items this particular fulfillment is for
    returns:
    order, data:  tuple of the order object and response data if successful.
    '''
    fb_meta = FacebookMetadata.objects.get(store=order.store)
    token = fb_meta.token_info
    url = settings.BASE_API_URL + order.ext_order_id + '/shipments'
    body = {
        'access_token': token,
        'items': items or get_order_items(order),
        'tracking_info': {
            'carrier': carrier,
            'tracking_number': tracking_number,
        },
        'idempotency_key': get_idempotency_key(),
    }
    res = requests.post(url, json=body)
    data = res.json()
    if not data.get("success", False):
        print(json.dumps(res.json(), indent=2))
        return None, None

    update_order_fulfillment_state(order, OrderFulfillmentState.FULLY_FULFILLED)
    update_order_state(order, OrderStatus.COMPLETED)
    return order, data


def get_order_items(order):
    ''' get retailer_id and quantity for all items in an order

    params:
    order: order object
    returns:
    items: list of dicts of product ids and quantities of said product in the order
    '''
    items = OrderItem.objects.filter(order=order)
    items = [{"retailer_id": i.product.id, "quantity": i.quantity} for i in items]
    return items


def cancel_order_by_id(order_id, cancel_reason, restock_items:bool = False, items=None):
    ''' Cancel an order by id
    NOTE: currently only cancels an order COMPLETELY

    params:
    order_id: id of the Order to cancel
    cancel_reason: CancellationReasonCode
    restock_items: set True if inventory should be restocked on successful cancel
    items: the subset of items this particular cancellation is for
    returns:
    order, data:  tuple of the order object and response data if successful.
    '''
    order = Order.objects.get(id=order_id)
    return cancel_order(order, CancellationReasonCode[cancel_reason], restock_items, items)


def cancel_order(order, cancel_reason:CancellationReasonCode, restock_items:bool = False, items=None):
    ''' Cancel an order
    NOTE: currently only cancels an order COMPLETELY

    params:
    order: the Order to cancel
    cancel_reason: CancellationReasonCode
    restock_items: set True if inventory should be restocked on successful cancel
    items: the subset of items this particular cancellation is for
    returns:
    order, data:  tuple of the order object and response data if successful.
    '''
    fb_meta = FacebookMetadata.objects.get(store=order.store)
    token = fb_meta.token_info
    url = settings.BASE_API_URL + order.ext_order_id + '/cancellations'
    body = {
        'access_token': token,
        'idempotency_key': get_idempotency_key(),
        'cancel_reason': {
            'reason_code': str(cancel_reason.name),
            'reason_description': str(cancel_reason.label),
        },
        'restock_items': restock_items,
    }
    if items:
        body['items'] = items
    res = requests.post(url, json=body)
    data = res.json()
    if not data.get("success", False):
        print(json.dumps(res.json(), indent=2))
        return None, None

    update_order_cancel_state(order, OrderCancellationState.FULLY_CANCELLED)
    update_order_state(order, OrderStatus.COMPLETED)
    return order, data


def refund_order_by_id(order_id, reason_code, items=None):
    ''' Refund an order by id
    NOTE: currently only refund an order COMPLETELY

    params:
    order_id: id of the Order to refund
    reason_code: refund reason code
    items: the subset of items this particular refund is for
    returns:
    order, data:  tuple of the order object and response data if successful.
    '''
    order = Order.objects.get(id=order_id)
    return refund_order(order, reason_code, items)


def refund_order(order, reason_code, items=None):
    ''' Refund an order
    NOTE: currently only refund an order COMPLETELY

    params:
    order: the Order to refund
    reason_code: refund reason code
    items: the subset of items this particular refund is for
    returns:
    order, data:  tuple of the order object and response data if successful.
    '''
    fb_meta = FacebookMetadata.objects.get(store=order.store)
    token = fb_meta.token_info
    url = settings.BASE_API_URL + order.ext_order_id + '/refunds'
    body = {
        'access_token': token,
        'idempotency_key': get_idempotency_key(),
        'reason_code': reason_code,
    }
    if items:
        body['items'] = items
    res = requests.post(url, json=body)
    data = res.json()
    if not data.get("success", False):
        print(json.dumps(res.json(), indent=2))
        return None, None

    update_order_refund_state(order, OrderRefundState.FULLY_REFUNDED)
    update_order_state(order, OrderStatus.COMPLETED)
    return order, data
