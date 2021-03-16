# Copyright 2004-present, Facebook. All Rights Reserved.
from django.db import models
from core.models import BaseModel


class Customer(BaseModel):
    """Represent a single customer instance

    fields:
    store: the store this customer belongs to
    full_name: customer full name
    email: customer email
    addr: customer shipping addr
    """

    store = models.ForeignKey("shop.Store", null=True, on_delete=models.SET_NULL)
    full_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    addr = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.full_name
