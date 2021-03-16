# Copyright 2004-present, Facebook. All Rights Reserved.
import datetime
import json

import requests
from core.models.utils import datetime_utc_now_with_tz
from django.conf import settings
from fb_metadata.models import FacebookMetadata
from shop.models import Store


def retrieveAndStoreFBEInstallationInfo(
    fbe_external_business_id, access_token, expires_in
):
    """
    This method gets information from the FBE Installation API regarding the assets that were assigned to
    a particular business during the FBE flow. It then updates the related fields on the FacebookMetadata
    object.

    params:
    fbe_external_business_id: a unique id used by the platform to identify the business on Facebook
    access_token: a token that allows access to the API endpoint
    expires_in: when the access_token expires which is stored in the FacebookMetadata object

    returns:
    store id associated with this FacebookMetadata object
    """
    info = requests.get(
        settings.FBE_INFO_API_URL.format(fbe_external_business_id, access_token)
    ).json()["data"][0]

    metadata = FacebookMetadata.objects.get(
        fbe_external_business_id=fbe_external_business_id
    )

    # update access token
    metadata.token_info = access_token
    metadata.token_creation_date = datetime_utc_now_with_tz()
    metadata.token_expiration_date = datetime_utc_now_with_tz() + datetime.timedelta(
        0, expires_in
    )

    # update fbe specific metadata
    if "pixel_id" in info.keys():
        metadata.fbe_pixel_id = info["pixel_id"]
    if "business_manager_id" in info.keys():
        metadata.fbe_business_manager_id = info["business_manager_id"]
    if "ad_account_id" in info.keys():
        metadata.fbe_ad_account_id = info["ad_account_id"]
    if "catalog_id" in info.keys():
        metadata.fb_catalog_id = info["catalog_id"]
    if "pages" in info.keys():
        metadata.fbe_page_id = info["pages"][0]
    if "instagram_profiles" in info.keys():
        metadata.fbe_ig_profile_id = info["instagram_profiles"][0]
    if "commerce_merchant_settings_id" in info.keys():
        metadata.commerce_account_id = info["commerce_merchant_settings_id"]

    metadata.fb_shop_setup_status = "SETUP"
    metadata.save()
    return metadata.store.id


def getFBEOnboardingDetails(store_id):
    """
    This method gets a Store's corresponding FacebookMetadata object. If the store does not have one, it returns none.

    params:
    store_id: the id for the Store to get the FacebookMetadata of

    returns:
    either the FacebookMetadata object for a particular Store or None if one doesn't exist
    """
    store = Store.objects.get(id=store_id)

    metadata = FacebookMetadata.objects.filter(store=store)
    if len(metadata) == 0:
        return None
    else:
        return metadata[0]


def generateFBEOnboardingURL(metadata: FacebookMetadata):
    """
    This method generates the FBE Onboarding URL to start the FBE Onboarding flow

    params:
    metadata: The FacebookMetadata object for the store that should be onboarded

    returns:
    the url for FBE onboarding
    """
    # permissions to grant FB
    # Optionally, you can also use the "manage_business_extension,ads_management" permissions here
    # as stated in the FBE documentation
    # https://developers.facebook.com/docs/marketing-api/fbe/fbe2/guides/authentication#biz_login_via_url
    _SCOPE = "manage_business_extension,catalog_management"

    # build the json obj to be serialized for url
    extras = {
        "setup": {
            "external_business_id": metadata.fbe_external_business_id,
            "timezone": metadata.fbe_timezone,
            "currency": metadata.fbe_currency,
            "business_vertical": metadata.fbe_business_vertical,
            "domain": settings.DOMAIN,
            "channel": "COMMERCE",
            "test_config": {
                "test_commerce_account": True,
            },
        },
        "business_config": {
            "business": {"name": metadata.store.name},
            "page_shop": {"enabled": True, "visible_product_count": 5},
        },
        "repeat": False,
    }
    print("FBE Extras:", extras)

    # turn our object into json string for the URL
    extras_string = json.dumps(extras)

    # the state string helps us match our fb metadata object to the shop after callback
    state_string = "fbe_external_business_id=" + metadata.fbe_external_business_id

    # substitute values into the FBE_ONBOARDING_URL string
    fb_url = settings.FBE_ONBOARDING_URL.format(
        settings.APP_ID,
        settings.REDIRECT_URI,
        _SCOPE,
        state_string,
        extras_string,
    )

    return fb_url
