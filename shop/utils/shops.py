# Copyright 2004-present, Facebook. All Rights Reserved.
from catalog.utils import create_catalog
from django.contrib.auth.models import User
from shop.models import Store, MerchantToStores


def createStore(store_name, user, unique_business_id):
    """
    This method creates a Store in the database and links it to the user who created it.

    params:
    store_name: the name of the business/store being created (String)
    user: the current user creating the store (User)
    unique_business_id: a platform's unique identifier for a store connected to Facebook

    returns:
    Store object that was created in DB
    """
    # creates a Store and a blank catalog for the Store
    store = Store(name=store_name, merchant=user)
    if unique_business_id:
        store.unique_business_id = unique_business_id
    store.save()

    create_catalog(store, True)

    # link Store with user who created it
    linkUser = MerchantToStores(
        merchant=user,
        store=store,
    )
    linkUser.save()

    return store


def canViewThisStore(store_id, user_id):
    """
    This method checks if a particular user can view a store

    params:
    store_id: the id of the Store
    user_id: the id of the User who needs permission

    returns:
    a boolean; returns True if a user owns this store or can view it
    """
    user = User.objects.get(id=user_id)

    if user.is_superuser:
        return True
    try:
        store = MerchantToStores.objects.get(store_id=store_id)
        if user.id == store.merchant.id:
            return True
        else:
            return False
    except Exception as e:
        print("ERROR:", str(e))
        return False
