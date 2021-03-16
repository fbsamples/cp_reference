# Copyright 2004-present, Facebook. All Rights Reserved.
from django.contrib import admin

# Register your models here so they show up in the Admin panel.
from .models import (
    Store,
    Setting,
    MerchantToStores,
)

admin.site.register(Store)
admin.site.register(Setting)
admin.site.register(MerchantToStores)
