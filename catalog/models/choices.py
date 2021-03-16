# Copyright 2004-present, Facebook. All Rights Reserved.
from django.db import models
from django.utils.translation import gettext_lazy


class Availability(models.TextChoices):
    """ Product availability statuses

    IN_STOCK: item will ship immediately
    AVAILABLE: item will ship in max 2 weeks
    OUT_OF_STOCK: item is not in current stock
    DISCONTINUED: item is discontinued
    """

    IN_STOCK = "IN", gettext_lazy("in stock")
    AVAILABLE = "AVA", gettext_lazy("available")
    OUT_OF_STOCK = "OUT", gettext_lazy("out of stock")
    DISCONTINUED = "DIS", gettext_lazy("discontinued")


class Visibility(models.TextChoices):
    """ Product Visibility

    published - Default. Enables the item to be visible to users.\n
    staging - Item remains hidden from the user, but present in the catalog.\n

    Items in staging mode are not visible to buyers, and are not available for product tagging on Instagram, nor for dynamic ads.
    """
    PUBLISHED = "PUBLISHED", gettext_lazy("Published")
    STAGING = "STAGING", gettext_lazy("Staging")


class Condition(models.TextChoices):
    """ Product condition labels such as NEW or USED """

    NEW = "NEW", gettext_lazy("New")
    USED = "USED", gettext_lazy("Used")
    REFURB = "REFURB", gettext_lazy("Refurbished")
