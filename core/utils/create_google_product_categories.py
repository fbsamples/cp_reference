# Copyright 2004-present, Facebook. All Rights Reserved.
import json
import os

import requests
from django.conf import settings


def create_google_product_categories():
    """ This method creates a JSON of the google product categories that is used to populate the dropdown """
    r = requests.get(
        "https://www.google.com/basepages/producttype/taxonomy-with-ids.en-US.txt"
    )

    result = {}

    for category in r.text.strip().split("\n")[1:]:
        line = category.split("-", 1)

        number = int(line[0].strip())

        # Format Category > Sub-category > Sub sub-category > ...
        full_category = line[1].strip()

        # Break up full_catagory
        separated = full_category.split(">")
        current = result

        for piece in separated:
            piece = piece.strip()

            if piece.strip() not in current.keys():
                # need to add this category
                current[piece] = {"id": number}
            current = current[piece]

    with open(
        os.path.join(settings.BASE_DIR, "static", "js", "google_product_categories.js"),
        "w",
        encoding="utf-8",
    ) as file:
        file.write("google_product_categories = " + json.dumps(result))
