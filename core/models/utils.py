# Copyright 2004-present, Facebook. All Rights Reserved.
from datetime import datetime, timezone

def datetime_utc_now_with_tz():
    '''UTC now helper function
    db model datetime field default values must be a function so
    "now" will be when field is updated/created rather than when
    module is imported.  so it must take no parameters.
    datetime.datetime.utcnow works, but has no tz value and triggers warning in django
    instead we just wrap datetime.datetime.now and pass in a timezone.
    '''
    return datetime.now(timezone.utc)
