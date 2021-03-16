# Copyright 2004-present, Facebook. All Rights Reserved.
from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

urlpatterns = [
    path("store/<int:storeId>/fbe", login_required(views.fbe), name="fbe"),
    # onboarding
    path("callback", views.fbe_callback, name="fbe_callback"),
    path(
        "store/<int:storeId>/facebook_settings",
        login_required(views.viewFbSettings),
        name="viewFbSettings",
    ),
    path(
        "store/<int:storeId>/tokens",
        login_required(views.tokenSettings),
        name="tokenSettings",
    ),
]
