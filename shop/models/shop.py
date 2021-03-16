# Copyright 2004-present, Facebook. All Rights Reserved.
import uuid

from django.db import models
from django.contrib.auth.models import User

from core.models import BaseModel
from core.models.utils import datetime_utc_now_with_tz

class Store(BaseModel):
    """Represents a single shop.

    fields:
    catalog_id: the current active catalog for this store
    historical_catalogs: csv of inactive catalog ids
    """
    unique_business_id = models.CharField(
        max_length=100, unique=True, default=uuid.uuid4
    )
    merchant = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=datetime_utc_now_with_tz, blank=True)
    catalog_id = models.OneToOneField(
        "catalog.Catalog",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="catalog",
    )
    historical_catalogs = models.TextField(blank=True, default="")

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['merchant', 'name'], name='unique_store_name_for_merchant')
        ]


class Setting(BaseModel):
    """ The settings info for a shop, such as shipping or tax info"""

    store = models.OneToOneField(
        Store,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    shipping = models.TextField(blank=True, null=True)
    tax = models.TextField(blank=True, null=True)
    return_policy = models.TextField(blank=True, null=True)
    payout = models.TextField(blank=True, null=True)
    contact = models.TextField(blank=True, null=True)
