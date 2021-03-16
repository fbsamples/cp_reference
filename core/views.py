# Copyright 2004-present, Facebook. All Rights Reserved.
import os

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
from fb_metadata.utils import getFBEOnboardingDetails
from shop.models import Store

from .utils import create_google_product_categories


def index(request):
    template = loader.get_template("core/index.html")
    context = {}
    return HttpResponse(template.render(context, request))


def viewAsyncTasks(request, storeId):
    """view listing all available scheduled async tasks for the store
    user can manually trigger these tasks here as well
    """
    tasks = [
        {
            "name": "Fetch Orders",
            "description": "List and acknowledge orders",
            "view_method": "listAndAckOrders",
        },
        {
            "name": "Sync Catalog",
            "description": "Load all items in local catalog and sync to FB, inserting missing items, updating existing ones, does not delete",
            "view_method": "syncCatalog",
        },
    ]
    store = Store.objects.get(id=storeId)
    metadata = getFBEOnboardingDetails(store.id)
    context = {
        "tasks": tasks,
        "store": store,
        "fb_metadata": metadata,
    }
    return render(request, "core/async_tasks.html", context)


def createGoogleProductCategories(request):
    """ view method to create the google_product_categories.js file """
    create_google_product_categories()
    return redirect("index")


def handler400(request, ex):
    return render(request, "400.html")


def handler403(request, ex):
    return render(request, "403.html")


def handler404(request, ex):
    return render(request, "404.html")


def handler500(request):
    return render(request, "500.html")
