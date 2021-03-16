# Copyright 2004-present, Facebook. All Rights Reserved.
from core.models import BaseModel
from django.contrib.auth.models import User
from django.db import models

from .shop import Store


class MerchantToStores(BaseModel):
    """
    Maps a Merchant/User to the stores they've created.
    fields:
    merchant: a user on the platform
    store: the store the user owns/created
    """

    merchant = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL
    )  # if deleted, we still want to keep this connection
    store = models.ForeignKey(
        Store, null=True, on_delete=models.CASCADE
    )  # if a store is deleted, we want to remove this connection
