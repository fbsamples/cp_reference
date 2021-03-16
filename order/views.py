# Copyright 2004-present, Facebook. All Rights Reserved.
from django.contrib import messages
from django.shortcuts import render, redirect

from shop.models import Store
from shop.utils import canViewThisStore
from fb_metadata.utils import getFBEOnboardingDetails
from .forms import (
    FulfillOrderForm,
)
from .models.choices import CancellationReasonCode, RefundReasonCode
from .tasks import (
    fetch_orders_async,
    fulfill_order_async,
    cancel_order_async,
    refund_order_async,
)
from .utils import (
    getOrderList,
    getOrderInformation,
)

def listAndAckOrders(request, storeId):
    ''' View method to call the async task to list and acknowledge orders '''
    fetch_orders_async.delay(storeId)
    return redirect("viewOrders", storeId)


def viewOrders(request, storeId):
    ''' view method for viewing list of orders for a store with storeId '''
    if canViewThisStore(storeId, request.user.id):
        store = Store.objects.get(id=storeId)
        metadata = getFBEOnboardingDetails(store.id)

        # for each order, get customer information, order information, and orderItem information
        context = {
            "store": store,
            "fb_metadata": metadata,
            "orders": getOrderList(store.id),
        }

        return render(request, "order/orders.html", context)
    else:
        return render(request, "403.html")


def viewOrder(request, storeId, orderId):
    ''' view method for viewing a particular order for a store '''
    if canViewThisStore(storeId, request.user.id):
        orderInfo = getOrderInformation(orderId)
        store = Store.objects.get(id=orderInfo["storeId"])
        metadata = getFBEOnboardingDetails(store.id)

        context = {
            **orderInfo,
            "store": store,
            "fb_metadata": metadata,
        }

        return render(request, "order/order.html", context)
    else:
        return render(request, "403.html")


ASYNCTASK_MSG = "{} action is being processed async in background.  Check back in a few minutes."

def cancelOrder(request, storeId, orderId):
    ''' View method to call the async task to cancel and order for a store '''
    cancel_order_async.delay(
        orderId, CancellationReasonCode.CUSTOMER_REQUESTED, restock_items=True
    )
    messages.warning(request, ASYNCTASK_MSG.format("Cancellation"))
    return redirect("viewOrder", storeId, orderId)


# fulfill order view, where you can add carrier etc
def fulfillOrder(request, storeId, orderId):
    ''' View to fulfill order, where you can add carrier and tracking number'''
    if canViewThisStore(storeId, request.user.id):
        store = Store.objects.get(id=storeId)

        if request.method == "POST":
            # Create a form instance and populate it with data from the request (binding):
            form = FulfillOrderForm(request.POST)

            # Check if the form is valid:
            if form.is_valid():
                carrier = form.cleaned_data["carrier"]
                tracking_number = form.cleaned_data["tracking_number"]
                # NOTE Currently only fulfilling orders fully
                fulfill_order_async.delay(orderId, carrier, tracking_number)
                messages.warning(request, ASYNCTASK_MSG.format("Fulfillment"))
                return redirect("viewOrder", storeId, orderId)

        form = FulfillOrderForm()
        breadcrumbs = [
            (store.name, "viewStore", store.id),
            ("Orders", "viewOrders", store.id),
            ("Order {}".format(orderId), "viewOrder", (storeId, orderId)),
        ]
        context = {
            "form": form,
            "page_title": "Fulfill Order",
            "breadcrumbs": breadcrumbs,
            "button": "Fulfill",
        }
        return render(request, "core/update.html", context)
    else:
        return render(request, "403.html")


def refundOrder(request, storeId, orderId):
    ''' view method to call the async task to refund an order '''
    refund_order_async.delay(orderId, RefundReasonCode.BUYERS_REMORSE)
    messages.warning(request, ASYNCTASK_MSG.format("Refund"))
    return redirect("viewOrder", storeId, orderId)
