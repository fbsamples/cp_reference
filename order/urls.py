# Copyright 2004-present, Facebook. All Rights Reserved.
from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

urlpatterns = [
    # view orders list
    path(
        "store/<int:storeId>/orders",
        login_required(views.viewOrders),
        name="viewOrders",
    ),
    # async: list and acknowledge orders
    path(
        "store/<int:storeId>/orders/list_and_ack",
        login_required(views.listAndAckOrders),
        name="listAndAckOrders",
    ),
    # order details
    path(
        "store/<int:storeId>/order/<int:orderId>",
        login_required(views.viewOrder),
        name="viewOrder",
    ),
    # async: cancel order
    path(
        "store/<int:storeId>/order/<int:orderId>/cancel",
        login_required(views.cancelOrder),
        name="cancelOrder",
    ),
    # async: fulfill order
    path(
        "store/<int:storeId>/order/<int:orderId>/fulfill",
        login_required(views.fulfillOrder),
        name="fulfillOrder",
    ),
    # async: refund order
    path(
        "store/<int:storeId>/order/<int:orderId>/refund",
        login_required(views.refundOrder),
        name="refundOrder",
    ),
]
