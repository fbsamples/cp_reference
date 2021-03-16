# Copyright 2004-present, Facebook. All Rights Reserved.
from django.contrib import admin

# Register your models here.
from .models import (
    Customer,
    Order,
    OrderItem,
)

admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderItem)
