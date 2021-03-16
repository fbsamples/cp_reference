# Copyright 2004-present, Facebook. All Rights Reserved.
from django.contrib.auth.decorators import login_required
from django.urls import path, include

from . import views

urlpatterns = [
    path("", login_required(views.index), name="index"),
    path(
        "store/<int:storeId>/async_tasks",
        login_required(views.viewAsyncTasks),
        name="viewAsyncTasks",
    ),
    path(
        "create_google_product_categories",
        login_required(views.createGoogleProductCategories),
        name="createGoogleProductCategories",
    ),
    # Order Management System (OMS)
    path("", include("order.urls")),
    # Catalogs
    path("", include("catalog.urls")),
    # Shops
    path("", include("shop.urls")),
    # Member
    path("", include("member.urls")),
    # facebook metadata related urls
    path("", include("fb_metadata.urls")),
]
