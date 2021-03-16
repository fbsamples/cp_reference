# Copyright 2004-present, Facebook. All Rights Reserved.
from django.db import models
from core.models import BaseModel
from shop.models import Store


class Collection(BaseModel):
    """Represents a single collection.
    A collection is a logical compilation of products, related by some criteria,
    eg "fall collection", "electronics", "gifts < $10" etc.
    A Collection is essentially a Product Set, its mainly to distinguish
    between commerce and ads prodcuts sets.

    fields:
    store: the store this collection belongs to
    """

    store = models.ForeignKey(Store, on_delete=models.CASCADE)

    def __str__(self):
        return "Collection for {} ({})".format(self.store.name, self.id)
