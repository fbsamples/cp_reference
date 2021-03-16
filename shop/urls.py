# Copyright 2004-present, Facebook. All Rights Reserved.
from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

urlpatterns = [
    # stores
    path("store/", login_required(views.viewStores), name="viewStores"),
    path(
        "store/create",
        login_required(views.createNewLocalStore),
        name="createNewLocalStore",
    ),
    path(
        "store/<int:storeId>/update",
        login_required(views.updateStore),
        name="updateStore",
    ),
    path("store/<int:storeId>", login_required(views.viewStore), name="viewStore"),
]
