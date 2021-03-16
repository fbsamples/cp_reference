# Copyright 2004-present, Facebook. All Rights Reserved.
import random

from django.db import transaction

from shop.models import Store
from catalog.models import Product
from .catalogs import create_product


@transaction.atomic
def create_dummy_products(store_id):
    ''' helper view method to populate a test shop with products (and variants) '''
    products = [
        {
            "title": "Jar",
            "desc": "Modern looking jar",
            "link": 225,
            "category_string": "Arts & Entertainment > Hobbies & Creative Arts > Homebrewing & Winemaking Supplies > Bottling Bottles",
            "category_id": "502980",
        },
        {
            "title": "Spoon",
            "desc": "Modern looking spoon set",
            "link": 23,
            "category_string": "Home & Garden > Kitchen & Dining > Tableware > Flatware > Spoons",
            "category_id": "3939",
        },
        {
            "title": "Cup",
            "desc": "Modern looking cup set",
            "link": 248,
            "category_string": "Home & Garden > Kitchen & Dining > Tableware > Drinkware > Beer Glasses",
            "category_id": "7568",
        },
        {
            "title": "Camera",
            "desc": "Full frame camera",
            "link": 250,
            "category_string": "Cameras & Optics > Cameras > Film Cameras",
            "category_id": "154",
        },
        {
            "title": "Glasses",
            "desc": "Italian glasses",
            "link": 26,
            "category_string": "Health & Beauty > Personal Care > Vision Care > Eyeglasses",
            "category_id": "524",
        },
        {
            "title": "Retro cups",
            "desc": "Retro style cups",
            "link": 30,
            "category_string": "Home & Garden > Kitchen & Dining > Tableware > Drinkware > Beer Glasses",
            "category_id": "7568",
        },
        {
            "title": "Micro third Camera",
            "desc": "Micro third camera",
            "link": 319,
            "category_string": "Cameras & Optics > Cameras > Film Cameras",
            "category_id": "154",
        },
        {
            "title": "Cup set",
            "desc": "Ceramic cups",
            "link": 326,
            "category_string": "Home & Garden > Kitchen & Dining > Tableware > Drinkware > Coffee & Tea Cups",
            "category_id": "6049",
        },
        {
            "title": "Vintage clock",
            "desc": "French vintage clock",
            "link": 357,
            "category_string": "Home & Garden > Decor > Clocks > Wall Clocks",
            "category_id": "3840",
        },
        {
            "title": "Gaming Keyboard GK-2",
            "desc": "Mechanical gaming keyboard",
            "link": 366,
            "category_string": "Electronics > Electronics Accessories > Computer Components > Input Devices > Keyboards",
            "category_id": "303",
        },
        {
            "title": "Kindle",
            "desc": "Read books anywhere",
            "link": 367,
            "category_string": "Electronics > Computers > Handheld Devices > E-Book Readers",
            "category_id": "3539",
        },
        {
            "title": "Book: Art of War",
            "desc": "Read books anywhere",
            "link": 464,
            "category_string": "Media > Books > Print Books",
            "category_id": "543543",
        },
        {
            "title": "Laptop: CCP",
            "desc": "High performance laptop",
            "link": 48,
            "category_string": "Electronics > Computers > Laptops",
            "category_id": "328",
        },
        {
            "title": "Plastic Hangers",
            "desc": "Premium plastic hangers",
            "link": 535,
            "category_string": "Home & Garden > Household Supplies > Storage & Organization > Clothing & Closet Storage > Hangers",
            "category_id": "631",
        },
    ]
    store = Store.objects.get(id=store_id)
    brand = store.name
    catalog = store.catalog_id
    for product in products:
        amount = random.randint(10, 100)
        dec = random.randint(0, 99)
        amount_str = "{}.{}".format(amount, dec)
        inventory = random.randint(99, 999)
        link = "https://picsum.photos/id/{}/200/300".format(product["link"])
        dummy_product = create_product(
            catalog,
            product["category_id"],
            product["category_string"],
            product["title"],
            product["desc"],
            amount_str,
            inventory,
            link,
            link,
            brand,
        )
        create_smaller_dummy_product_variant(dummy_product, store)


def create_smaller_dummy_product_variant(product:Product, store:Store):
    ''' helper method to create specifically a 'smaller' product variant based on a product, and make the orig_product 'large' '''
    create_product(
        store.catalog_id,
        product.google_product_category,
        product.google_product_category_string,
        "{} (Small)".format(product.title),
        "{}. Small.".format(product.description),
        product.amount,
        product.inventory,
        product.link,
        product.image_link,
        product.brand,
        product_group_name="{}ProductGroup".format(product.title),
        store=store,
        orig_product=product,
        existing_product_variation_updates={product.id: {"size": "Large"}},
        size="Small",
    )
