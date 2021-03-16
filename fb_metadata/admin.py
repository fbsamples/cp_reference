# Copyright 2004-present, Facebook. All Rights Reserved.
from django.contrib import admin

# Register your models here.
from .models import (
    FacebookMetadata,
)

admin.site.register(FacebookMetadata)
