# Copyright 2004-present, Facebook. All Rights Reserved.
from uuid import uuid4

def get_idempotency_key():
    ''' use uuid4 string as request idempotency key
    returns:
    str: a uuid4 as a string
     '''
    return str(uuid4())
