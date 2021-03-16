# Copyright 2004-present, Facebook. All Rights Reserved.
from shop.models import Store, MerchantToStores
from django.conf import settings


def app_name(request):
    return {"APP_NAME": settings.APP_NAME}


def allStoresContext(request):
    stores_data = {}
    if request.user.is_authenticated and request.user.is_superuser:
        stores = Store.objects.all()
        for store in stores:
            stores_data[store.id] = store.name
    elif request.user.is_authenticated:
        stores = MerchantToStores.objects.filter(merchant=request.user)
        for store in stores:
            stores_data[store.store.id] = store.store.name
    return {"user_all_stores": stores_data}
