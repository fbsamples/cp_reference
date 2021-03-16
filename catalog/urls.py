# Copyright 2004-present, Facebook. All Rights Reserved.
from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

urlpatterns = [
    # products
    path(
        "store/<int:storeId>/products/create",
        login_required(views.createProduct),
        name="createProduct",
    ),
    path(
        "store/<int:storeId>/product/<str:productId>/update",
        login_required(views.updateProduct),
        name="updateProduct",
    ),
    path(
        "store/<int:storeId>/products",
        login_required(views.viewProducts),
        name="viewProducts",
    ),
    path(
        "store/<int:storeId>/product/<str:productId>",
        login_required(views.viewProduct),
        name="viewProduct",
    ),
    # catalog
    path(
        "store/<int:storeId>/catalog/sync",
        login_required(views.syncCatalog),
        name="syncCatalog",
    ),
    # dummy products
    path(
        "store/<int:storeId>/create_dummy_products",
        login_required(views.createDummyProducts),
        name="createDummyProducts",
    ),
]
