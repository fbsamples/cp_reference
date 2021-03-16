# Copyright 2004-present, Facebook. All Rights Reserved.
from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

urlpatterns = [
    path("", login_required(views.notifications), name="notifications"),
]
