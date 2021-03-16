# Copyright 2004-present, Facebook. All Rights Reserved.
import json
import os
import sys

import requests
from core.models.utils import datetime_utc_now_with_tz
from core.tasks import sync_catalog_async
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from shop.models import Store
from shop.utils import canViewThisStore

from .forms import FbeOnboardingForm
from .models import FacebookMetadata
from .utils import (
    retrieveAndStoreFBEInstallationInfo,
    getFBEOnboardingDetails,
    generateFBEOnboardingURL,
)


def fbe(request, storeId):
    """ This view shows the form for entering the FBE flow and then redirects the user on submit to FBE """
    if canViewThisStore(storeId, request.user.id):
        store = Store.objects.get(id=storeId)
        if request.method == "POST":
            metadata_obj = FacebookMetadata.objects.filter(store=store).first()
            if not metadata_obj.fbe_external_business_id:
                metadata_obj.fbe_external_business_id = store.unique_business_id
                metadata_obj.save()

            # generate the FBE onboarding URL
            fb_url = generateFBEOnboardingURL(metadata_obj)
            print("FBE Onboarding URL:", fb_url)

            # redirect to FBE onboarding
            return HttpResponseRedirect(fb_url)

        # check if already connected
        existing_metadata = FacebookMetadata.objects.filter(store=store).first()
        if (
            existing_metadata
            and existing_metadata.fbe_external_business_id == store.unique_business_id
        ):
            return redirect("viewFbSettings", storeId)

        # If this is a GET (or any other method) create the default form.
        form = FbeOnboardingForm(
            initial={
                "business_name": store.name,
            }
        )
        context = {
            "store": store,
            "form": form,
        }
        return render(request, "fb_metadata/fbe.html", context)
    else:
        return render(request, "403.html")


def fbe_callback(request):
    """ only callback route; stores the access_token, expiration date, and time valid returned from API call """

    # store the info
    try:
        res = requests.get(settings.GET_ACCESS_TOKEN_URL + request.GET.get("code"))
        if not res.ok:
            print("request error:", json.dumps(res.json()))
            return HttpResponse(
                "Failed to retrieve access token. Check the log for more information."
            )
        access_token = res.json()["access_token"]
        expires_in = res.json()["expires_in"]

        # get the fbe_external_business_id since this should be unique
        state = request.GET.get("state").split("=")
        fbe_external_id = state[1]  # split to get the right value
        print(fbe_external_id)

        # this gets additional FB information like pixel id, cms id, etc.
        store_id = retrieveAndStoreFBEInstallationInfo(
            fbe_external_id, access_token, expires_in
        )

        # as soon as fbe is completed, we should sync catalog
        sync_catalog_async.delay(store_id)

        # redirect to the FB Settings page
        return redirect("viewFbSettings", store_id)
    except KeyError as err:
        print("KEY ERROR:", err)
        return HttpResponse(
            "Reponse did not have expected values! Check the log for more information."
        )
    except TypeError:
        if request.GET.get("error"):
            # user cancelled FBE flow, return them to form
            # get the fbe_external_business_id since this should be unique
            state = request.GET.get("state").split("=")
            fbe_external_id = state[1]  # split to get the right value
            print(fbe_external_id)

            store = FacebookMetadata.objects.get(
                fbe_external_business_id=fbe_external_id
            ).store

            return redirect("fbe", store.id)
        else:
            return HttpResponse("The callback requires a code or error parameter.")
    except BaseException:
        print("Unexpected Error:", sys.exc_info()[0])
        return HttpResponse("Something went wrong. Check the logs.")


def viewFbSettings(request, storeId):
    """ This view shows the FB Settings page """
    if canViewThisStore(storeId, request.user.id):
        store = Store.objects.get(id=storeId)
        metadata = getFBEOnboardingDetails(storeId)
        if metadata is None:
            return redirect("fbe", storeId)

        # create fb_url when metadata.commerce_account_id doesn't exist
        fb_url = ""
        if not metadata.commerce_account_id:
            fb_url = generateFBEOnboardingURL(metadata)

        context = {"store": store, "fb_metadata": metadata, "fb_url": fb_url}
        return render(request, "fb_metadata/fb_settings.html", context)
    else:
        return render(request, "403.html")


def tokenSettings(request, storeId):
    """ This view shows the page displaying token information and allows user to change token from System User token to User token """
    store = Store.objects.get(id=storeId)
    metadata = getFBEOnboardingDetails(store.id)
    if request.method == "POST":
        fb_meta = FacebookMetadata.objects.get(store=store)
        url = settings.SYSTEM_USER_TOKEN_API_URL.format(fb_meta.fbe_business_manager_id)
        _SCOPE = "business_management,manage_business_extension,catalog_management,commerce_manage_accounts"
        data = {
            "app_id": settings.APP_ID,
            "access_token": fb_meta.token_info,
            "scope": _SCOPE,
            "fbe_external_business_id": fb_meta.fbe_external_business_id,
        }
        res = requests.post(url, data=data)
        system_user_access_token = res.json()["access_token"]

        # update access token
        fb_meta.token_info = system_user_access_token
        fb_meta.token_creation_date = datetime_utc_now_with_tz()
        fb_meta.token_expiration_date = datetime_utc_now_with_tz() + relativedelta(
            years=10
        )
        fb_meta.token_type = FacebookMetadata.GraphUserTokenType.SYSTEM_USER
        fb_meta.save()

    context = {"store": store, "fb_metadata": metadata}
    return render(request, "fb_metadata/tokens.html", context)
