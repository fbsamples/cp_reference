# Copyright 2004-present, Facebook. All Rights Reserved.
from django.db import models
from core.models import BaseModel
from shop.models import Store


class Catalog(BaseModel):
    """Represents a single catalog.
    A catalog represents the totality of products available on a shop.
    A catalog can contain products and Product Sets

    fields:
    store: the store this catalog belongs to
    feed_id: the feed api id to use for syncing catalogs (DEPRECATED)
    """

    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    feed_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return "Catalog for {}. id={}".format(self.store.name, self.id)

class CatalogItem(BaseModel):
    """ Represents one unique product item that is in a catalog"""

    catalog = models.ForeignKey(Catalog, on_delete=models.CASCADE)
    product = models.OneToOneField(
        "Product",
        on_delete=models.CASCADE,
        primary_key=True,
    )

class CatalogItemGroup(BaseModel):
    """ Represents one product group that is in a catalog"""

    catalog = models.ForeignKey(Catalog, on_delete=models.CASCADE)
    product_group = models.OneToOneField(
        "ProductGroup",
        on_delete=models.CASCADE,
        primary_key=True,
    )
