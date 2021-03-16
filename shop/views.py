# Copyright 2004-present, Facebook. All Rights Reserved.
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
from fb_metadata.models import FacebookMetadata
from fb_metadata.utils import getFBEOnboardingDetails

from .forms import StoreCreationForm, UpdateStoreForm
from .models import Store, MerchantToStores
from .utils import createStore, canViewThisStore


def createNewLocalStore(request):
    """ view for creating a local store """
    if request.method == "POST":
        form = StoreCreationForm(request.POST)
        if form.is_valid():
            try:
                store = Store.objects.get(
                    name=form.cleaned_data["business_name"], merchant=request.user
                )
                print("Store found")
                # cannot use context on redirect so use messages framework
                messages.warning(
                    request,
                    "You have been redirected to an existing shop with the same name (new shop not created).",
                )
            except Exception:
                print("Store not found.  Creating...")
                unique_business_id = form.cleaned_data["unique_business_id"]
                store = createStore(
                    form.cleaned_data["business_name"],
                    request.user,
                    unique_business_id=unique_business_id or None,
                )

                # Creates the initial metadata object in the DB
                metadata_obj = FacebookMetadata(
                    store=store,
                    fbe_timezone=form.cleaned_data["timezone"],
                    fbe_currency=form.cleaned_data["currency"],
                    fbe_business_vertical="ECOMMERCE",
                    fbe_domain=settings.DOMAIN,
                    fbe_channel="COMMERCE",
                )
                metadata_obj.save()
                print("Created metadata for store")
            return redirect("viewStore", store.id)
        else:  # form is not valid
            return HttpResponseBadRequest()
    else:  # GET request
        form = StoreCreationForm()
        context = {
            "form": form,
        }
    return render(request, "shop/create_store.html", context)


def viewStore(request, storeId):
    """ view for viewing individual store """
    if canViewThisStore(storeId, request.user.id):
        store = Store.objects.get(id=storeId)
        metadata = getFBEOnboardingDetails(store.id)
        context = {"store": store, "fb_metadata": metadata}
        return render(request, "shop/store.html", context)
    else:
        return render(request, "403.html")


def viewStores(request):
    """ view for viewing list of stores """
    # first get all the stores
    stores = []
    if request.user.is_superuser:
        stores = Store.objects.all().values()
    else:
        merchant_stores = MerchantToStores.objects.filter(merchant=request.user)
        stores = [merchant.store for merchant in merchant_stores]

    # then add to context and display on page
    context = {"stores": list(stores)}
    return render(request, "shop/stores.html", context)


def updateStore(request, storeId):
    """ view for updating store """
    if canViewThisStore(storeId, request.user.id):
        # get the corresponding store
        store = Store.objects.get(id=storeId)
        metadata = getFBEOnboardingDetails(store.id)

        if request.method == "POST":
            # Create a form instance and populate it with data from the request (binding):
            form = UpdateStoreForm(request.POST)

            # Check if the form is valid:
            if form.is_valid():
                store.name = form.cleaned_data["business_name"]
                store.save()
                return redirect("viewStore", storeId)

        form = UpdateStoreForm(initial={"business_name": store.name})

        breadcrumbs = [(store.name, "viewStore", store.id)]

        context = {
            "form": form,
            "store": store,
            "fb_metadata": metadata,
            "page_title": "Update Shop",
            "breadcrumbs": breadcrumbs,
            "button": "Update",
        }

        return render(request, "core/update.html", context)
    else:
        return render(request, "403.html")
