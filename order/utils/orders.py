# Copyright 2004-present, Facebook. All Rights Reserved.
import json

from shop.models import Store
from catalog.models import Product
from order.models import Customer, Order, OrderItem
from order.models.choices import (
    OrderCancellationState,
    OrderFulfillmentState,
    OrderRefundState,
)


def getOrderList(storeId):
    ''' get info for orders list view for a store by store id

    params:
    storeId: Store id
    returns:
    order_list: list of dicts of parsed order info
    '''
    store = Store.objects.get(id=storeId)
    orders = list(Order.objects.filter(store=store).order_by("-created"))
    order_list = [getOrderObjInfo(order) for order in orders]
    return order_list


def can_fulfill_order(order):
    ''' check if order can be fulfilled
    params:
    order: order object
    returns:
    bool: returns True if order is in a fulfillable state
    '''
    return not (
        order.order_cancellation_state == OrderCancellationState.FULLY_CANCELLED
        or order.order_fulfillment_state == OrderFulfillmentState.FULLY_FULFILLED
    )


def can_cancel_order(order):
    ''' check if order can be cancelled
    params:
    order: order object
    returns:
    bool: returns True if order is in a cancellable state
    '''
    return not (
        order.order_cancellation_state == OrderCancellationState.FULLY_CANCELLED
        or order.order_fulfillment_state == OrderFulfillmentState.FULLY_FULFILLED
    )


def can_refund_order(order):
    ''' check if order can be refunded
    params:
    order: order object
    returns:
    bool: returns True if order is in a refundable state
    '''
    return not (
        order.order_refund_state == OrderRefundState.FULLY_REFUNDED
        or order.order_fulfillment_state == OrderFulfillmentState.NO_FULFILLMENT
    )


def getOrderInformation(orderId):
    ''' get info to display for a single order by orderId
    params:
    order_id: order id
    returns:
    dict: dict of parsed order info
    '''
    order = Order.objects.filter(id=orderId).first()
    return getOrderObjInfo(order)


def getOrderObjInfo(order:Order):
    ''' get display info for an order object

    params:
    order: order object
    returns:
    dict: dict of parsed order info
    '''
    return {
        **{
            "storeId": order.store_id,
            "ext_order_id": order.ext_order_id,
            "orderId": order.id,
            "created": order.created,
            "currency": order.currency,
            "status": "Issues with Order" if order.missing_items else order.get_order_status_display(),
            "refund_status": order.get_order_refund_state_display(),
            "cancellation_status": order.get_order_cancellation_state_display,
            "fulfillment_status": order.get_order_fulfillment_state_display(),
            "missing_items": order.missing_items,
            "can_fulfill": can_fulfill_order(order),
            "can_cancel": can_cancel_order(order),
            "can_refund": can_refund_order(order),
        },
        **getCustomerInfo(order.customer_id),
        **getOrderItemsForOrder(order.id),
    }


def getOrderItemsForOrder(orderId):
    ''' get order items and products associated with the order (also calculates total price)
    params:
    orderId: order id
    returns:
    dict: dict containing list of order items, and total price and count
    '''
    orderItems = OrderItem.objects.filter(order_id=orderId)
    orderItems_list = []
    totalPrice = 0
    totalItems = 0

    for item in orderItems:
        product = Product.objects.filter(id=item.product_id).values()[0]
        totalPrice += product["amount"] * item.quantity
        totalItems += item.quantity

        orderItems_list.append(
            {
                **{
                    "quantity": item.quantity,
                    "price_for_item": product["amount"] * item.quantity,
                },
                **product,
            }
        )

    return {
        "items": orderItems_list,
        "total_price": totalPrice,
        "total_items": totalItems,
    }


def getCustomerInfo(customerId):
    ''' gets customer information for a particular customerId
    params:
    customerId: customer id
    returns:
    dict of customer info
    '''
    customer = Customer.objects.filter(id=customerId).values()[0]

    customer["addr"] = json.loads(customer["addr"])

    return customer
