# Copyright 2004-present, Facebook. All Rights Reserved.
from django.db import models

class BusinessVertical(models.TextChoices):
    ''' business vertial choices. Used for FBE '''
    ECOMMERCE = 'ECOMMERCE'
    SERVICE = 'SERVICE'


class FBEChannel(models.TextChoices):
    ''' Channel choices. Used for FBE '''
    COMMERCE = 'COMMERCE'
    COMMERCE_OFFSITE = 'COMMERCE_OFFSITE'
