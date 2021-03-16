# Copyright 2004-present, Facebook. All Rights Reserved.
import os
import hashlib
import hmac

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from fb_metadata.utils import getFBEOnboardingDetails
from shop.models import Store
from .utils import processWebhookNotification
from .models import WebhookNotification

@csrf_exempt
def webhooks(request):
    ''' process webhooks '''
    if request.method == "POST":
        if "X-Hub-Signature" not in request.headers:
            return HttpResponseBadRequest()
        # Check the X-Hub-Signature header to make sure this is a valid request.
        fb_signature = request.headers["X-Hub-Signature"]
        signature = hmac.new(
            os.getenv("FB_APP_SECRET").encode(), request.body, hashlib.sha1
        )
        expected_signature = "sha1=" + signature.hexdigest()
        if not hmac.compare_digest(fb_signature, expected_signature):
            return HttpResponseForbidden("Invalid signature header")
        processWebhookNotification(request.body)

        return HttpResponse()
    if request.method == "GET":
        # Verification request
        # https://developers.facebook.com/docs/graph-api/webhooks/getting-started#event-notifications
        hub_mode = request.GET.get("hub.mode", "")
        hub_verify_token = request.GET.get("hub.verify_token", "")
        if hub_mode != "subscribe" or hub_verify_token != os.getenv(
            "FB_WEBHOOK_APP_TOKEN"
        ):
            return HttpResponseBadRequest()
        return HttpResponse(request.GET.get("hub.challenge", ""))

    # should not reach here
    return HttpResponseBadRequest()

def notifications(request, storeId):
    ''' View a list of previous webhook notifications we've received for this store'''
    store = Store.objects.get(id=storeId)
    notifications = WebhookNotification.objects.filter(store=store)
    metadata = getFBEOnboardingDetails(store.id)
    context = {
        "store" : store,
        "fb_metadata": metadata,
        "notifications": notifications,
    }
    return render(request, "webhook/notifications.html", context)
