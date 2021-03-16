# Copyright 2004-present, Facebook. All Rights Reserved.
from django.db import models


class BaseModel(models.Model):
    '''Models do not automatically enforce certain required field rules.
    This is intended behavior and will not be changed in Django.
    We are to run validation ourselves in each model.
    Overriding save in models.Model is one recommended way.
    In order for this to work the class must be marked abstract using the Meta class
    below.'''

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
