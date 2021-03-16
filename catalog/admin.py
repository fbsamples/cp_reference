# Copyright 2004-present, Facebook. All Rights Reserved.
from django.contrib import admin

# Register your models here.
from .models import (
    Catalog,
    CatalogItem,
    CatalogItemGroup,
    Product,
    Collection,
    ProductSet,
    ProductSetItem,
    ProductGroup,
    ProductGroupItem,
)

admin.site.register(Catalog)
admin.site.register(Collection)
admin.site.register(ProductSet)
admin.site.register(ProductGroup)
admin.site.register(Product)
admin.site.register(ProductGroupItem)
admin.site.register(ProductSetItem)
admin.site.register(CatalogItem)
admin.site.register(CatalogItemGroup)
