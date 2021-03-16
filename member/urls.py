# Copyright 2004-present, Facebook. All Rights Reserved.
from django.urls import path

from . import views

urlpatterns = [
    path("register", views.register, name="register"),
]
