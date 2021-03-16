# Copyright 2004-present, Facebook. All Rights Reserved.
from django.db import models
from core.models.utils import datetime_utc_now_with_tz
from core.models import BaseModel
from shop.models import Store
from shop.models.choices import Currency
from catalog.models import Product
from .customers import Customer
from .choices import OrderFulfillmentState, OrderCancellationState, OrderStatus, OrderRefundState


class Order(BaseModel):
    """A single order
    fields:
    Customer: person who placed the order
    store: the store this order was placed with
    """

    customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)
    store = models.ForeignKey(Store, null=True, on_delete=models.SET_NULL)
    # Facebook order id
    ext_order_id = models.CharField(max_length=50, default=None, null=True)
    # status of the order such as Fully Cancelled, Fully Fulfilled, Fully Refunded
    order_status = models.CharField(
        max_length=15,
        choices=OrderStatus.choices,
        default=OrderStatus.FB_CREATED,
    )
    # refund state such as partially or fully refunded
    order_refund_state = models.CharField(
        max_length=18,
        choices=OrderRefundState.choices,
        default=OrderRefundState.NO_REFUNDS,
    )
    # time order was created on the local db
    created = models.DateTimeField(default=datetime_utc_now_with_tz, blank=True)
    # last update time to this order entry
    last_updated = models.DateTimeField(default=datetime_utc_now_with_tz, blank=True)
    # estimated ship by date, optional
    ship_by_date = models.DateTimeField(null=True, blank=True)
    # Currency the order was placed in
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.USD,
    )
    billing_address = models.TextField(null=True, blank=True)
    # order fulfillment state such as not fulfilled or fully fulfilled
    order_fulfillment_state = models.CharField(
        max_length=19,
        choices=OrderFulfillmentState.choices,
        default=OrderFulfillmentState.NO_FULFILLMENT,
    )
    # order cancellation state such as fully cancelled
    order_cancellation_state = models.CharField(
        max_length=19,
        choices=OrderCancellationState.choices,
        default=OrderCancellationState.NO_CANCELLATION,
    )
    # flag to indicate item(s) in this order is no longer exist in local products
    # and the order is invalid and can only be cancelled.
    missing_items = models.BooleanField(default=False)


class OrderItem(BaseModel):
    """A single line item in an order
    fields:
    order: the order this item belongs to
    product: the actual product of this order item.
    quantity: the number of this item in the Order
    """

    order = models.ForeignKey(Order, null=True, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    quantity = models.PositiveIntegerField(default=1)
