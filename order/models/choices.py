# Copyright 2004-present, Facebook. All Rights Reserved.
from django.db import models
from django.utils.translation import gettext_lazy


class OrderStatus(models.TextChoices):
    """ Order statuses

    COMPLETED: order was fulfilled/shipped or completely cancelled.
    CONFIRMED_ORDER: successfully acked order.
    FB_CREATED: orders fetched from fb are in this state, and needs to be acked
    IN_PROGRESS: order processing has begun (partially fulfilled/cancelled).
    """
    COMPLETED = "COMPLETED", gettext_lazy("Completed")
    CONFIRMED_ORDER = "CONFIRMED_ORDER", gettext_lazy("Confirmed Order")
    FB_CREATED = "FB_CREATED", gettext_lazy("FB Created")
    IN_PROGRESS = "IN_PROGRESS", gettext_lazy("In progress")


class OrderRefundState(models.TextChoices):
    ''' Refund states and descriptions '''
    FULLY_REFUNDED = 'FULLY_REFUNDED', gettext_lazy("Fully refunded")
    NO_REFUNDS = 'NO_REFUNDS', gettext_lazy("No refunds")
    PARTIALLY_REFUNDED = 'PARTIALLY_REFUNDED', gettext_lazy("Partially refunded")


class OrderCancellationState(models.TextChoices):
    ''' Cancellation states and descriptions '''
    FULLY_CANCELLED = 'FULLY_CANCELLED', gettext_lazy("Fully cancelled")
    NO_CANCELLATION = 'NO_CANCELLATION', gettext_lazy("No cancellation")
    PARTIALLY_CANCELLED = 'PARTIALLY_CANCELLED', gettext_lazy("Partially cancelled")


class OrderFulfillmentState(models.TextChoices):
    ''' Fulfillment state and descriptions '''
    FULLY_FULFILLED = 'FULLY_FULFILLED', gettext_lazy("Fully fulfilled")
    NO_FULFILLMENT = 'NO_FULFILLMENT', gettext_lazy("No fulfillment")
    PARTIALLY_FULFILLED = 'PARTIALLY_FULFILLED', gettext_lazy("Partially fulfilled")


class RefundReasonCode(models.TextChoices):
    ''' Refund reason codes and descriptions '''
    BUYERS_REMORSE = 'BUYERS_REMORSE', gettext_lazy('Refunded by buyers remorse.')
    DAMAGED_GOODS = 'DAMAGED_GOODS', gettext_lazy('Refunded as goods were delivered damaged.')
    NOT_AS_DESCRIBED = 'NOT_AS_DESCRIBED', gettext_lazy('Product not as described.')
    QUALITY_ISSUE = 'QUALITY_ISSUE', gettext_lazy('Product had quality issues.')
    REFUND_REASON_OTHER = 'REFUND_REASON_OTHER', gettext_lazy('Other refund reason.')
    WRONG_ITEM = 'WRONG_ITEM', gettext_lazy('Wrong product delivered.')


class CancellationReasonCode(models.TextChoices):
    ''' Cancellation reason codes and descriptions '''
    CUSTOMER_REQUESTED = 'CUSTOMER_REQUESTED', gettext_lazy('Cancellation requested by the buyer.')
    OUT_OF_STOCK = 'OUT_OF_STOCK', gettext_lazy('Product is out of stock at fulfillment.')
    INVALID_ADDRESS = 'INVALID_ADDRESS', gettext_lazy('Unable to ship to address provided by the buyer.')
    SUSPICIOUS_ORDER = 'SUSPICIOUS_ORDER', gettext_lazy('Order is suspicious/possible fraud.')
    CANCEL_REASON_OTHER = 'CANCEL_REASON_OTHER', gettext_lazy('Other cancellation reason.')
