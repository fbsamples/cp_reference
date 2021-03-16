# Copyright 2004-present, Facebook. All Rights Reserved.
import os

from core.models import BaseModel
from django.conf import settings
from django.db import models
from shop.models import Store
from shop.models.choices import Currency

from .choices import BusinessVertical, FBEChannel


class FacebookMetadata(BaseModel):
    """All FB specific metadata the platform needs to store

    fields:
    store: store this set of metadata belongs to
    fbe_external_business_id: unique id for FB to identify this store
    fbe_business_vertical: always 'ECOMMERCE' for reference implementation
    fbe_domain: Domain used for Instagram manual approval. required for COMMERCE and COMMERCE_OFFSITE channels
    fbe_channel: Not optional for RI.  Only options are COMMERCE and COMMERCE_OFFSITE.
    fbe_pixel: Pixel ID for the user's existing Pixel that a partner can pass in to preselect for the user in the setup flow.
    """

    _FB_COMMERCE_MANAGER_URL = "https://www.facebook.com/commerce_manager/{}"
    _FB_FBE_MANAGEMENT_VIEW_URL = "https://www.facebook.com/facebook_business_extension/management/?app_id={}&external_business_id={}&tab=Commerce"
    _FB_BUSINESS_MANAGER_URL = "https://business.facebook.com/settings/?business_id={}"
    _FB_CATALOG_MANAGER_URL = "https://www.facebook.com/products/catalogs/{}/products"

    class GraphUserTokenType(models.TextChoices):
        USER = "USER"
        SYSTEM_USER = "SYSTEM_USER"

    store = models.OneToOneField(
        Store,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    # the Facebook commerce account id for the Store
    commerce_account_id = models.CharField(max_length=50, blank=True, null=True)
    # Not currently used, but should store webhook information for this metadata object
    webhook = models.TextField(blank=True, null=True)
    # Also not currently used
    app_info = models.TextField(blank=True, null=True)
    fbe_external_business_id = models.CharField(max_length=255, blank=True, default="")
    """ The following fields are needed when creating the URL to launch FBE """
    fbe_timezone = models.TextField(
        default="UTC",
    )
    fbe_currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.USD,
    )
    fbe_business_vertical = models.CharField(
        max_length=9,
        choices=BusinessVertical.choices,
        default="",
    )
    fbe_domain = models.CharField(
        max_length=255,
        default="",
    )
    fbe_channel = models.CharField(
        max_length=16,
        choices=FBEChannel.choices,
        default="",
    )
    """ The following fields are set after the FBE setup is complete.
    This information is needed for API calls and troubleshooting."""
    fbe_business_manager_id = models.CharField(max_length=50, blank=True, default="")
    fbe_ad_account_id = models.CharField(max_length=50, blank=True, default="")
    fbe_page_id = models.CharField(max_length=50, blank=True, default="")
    fbe_ig_profile_id = models.CharField(max_length=50, blank=True, default="")
    fbe_pixel_id = models.CharField(max_length=50, blank=True, default="")
    # including fb_catalog_id since this is the FB side catalog id as opposed to the local RI id
    fb_catalog_id = models.CharField(max_length=50, blank=True, default="")
    fb_shop_setup_status = models.CharField(max_length=12, blank=True, default="")
    fb_shop_payment_setup_status = models.CharField(
        max_length=12, blank=True, default=""
    )
    fb_shop_review_status = models.CharField(max_length=12, blank=True, default="")
    token_info = models.TextField(blank=True, null=True)
    token_creation_date = models.DateTimeField(null=True, blank=True)
    token_expiration_date = models.DateTimeField(null=True, blank=True)
    token_type = models.CharField(
        max_length=20,
        default=GraphUserTokenType.USER,
        choices=GraphUserTokenType.choices,
    )

    # The following properties generate URLs based on the current FacebookMetadata's other fields
    @property
    def commerce_manager_url(self):
        return self._FB_COMMERCE_MANAGER_URL.format(self.commerce_account_id)

    @property
    def business_manager_url(self):
        return self._FB_BUSINESS_MANAGER_URL.format(self.fbe_business_manager_id)

    @property
    def fbe_management_view_url(self):
        return self._FB_FBE_MANAGEMENT_VIEW_URL.format(
            settings.APP_ID, self.fbe_external_business_id
        )

    @property
    def catalog_manager_url(self):
        return self._FB_CATALOG_MANAGER_URL.format(self.fb_catalog_id)

    def __str__(self):
        return "Store: [{}] Commerce Account: [{}]".format(
            self.store, self.commerce_account_id
        )
