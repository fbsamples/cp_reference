# Copyright 2004-present, Facebook. All Rights Reserved.
import json
import requests

from django.conf import settings
from django.db import transaction
from django.urls import reverse

from shop.models import Store
from catalog.models import (
    Catalog,
    CatalogItem,
    CatalogItemGroup,
    Collection,
    ProductSet,
    ProductGroup,
    Product,
)

from fb_metadata.models import FacebookMetadata


@transaction.atomic
def create_catalog(store, update_store: bool = False):
    ''' create a catalog for a store

    params:
    store: store for which to create a catalog
    update_store: whether or not we want to update the store's default catalog to this new one
                  this is for supporting multiple catalogs in future
    '''
    catalog = Catalog(store=store)
    catalog.save()
    if update_store:
        store.catalog_id = catalog
        store.save()
    return catalog


@transaction.atomic
def create_collection(store):
    ''' create a collection for a store

    params:
    store: store for which to create a catalog
    '''
    collection = Collection(store=store)
    collection.save()
    return collection


@transaction.atomic
def create_product_set(catalog, collection: Collection = None):
    ''' create a product_set for a catalog

    params:
    catalog: catalog for which to create a product set
    collection: collection to assign to the product set
    '''
    product_set = ProductSet(catalog=catalog)
    if collection:
        product_set.collection = collection
    product_set.save()
    return product_set


@transaction.atomic
def create_product_group(product_set):
    ''' create a product group for a product_set

    params:
    product_set: product_set for which to create a product_group
    '''
    product_group = ProductGroup(product_set=product_set)
    product_group.save()
    return product_group


@transaction.atomic
def create_product(
    catalog: Catalog,
    google_product_category: str,
    google_product_category_string: str,
    title: str,
    description: str,
    amount: str,
    inventory: int,
    link: str,
    image_link: str,
    brand="custom",
    id=None,
    product_group=None,
    product_group_name=None,
    store=None,
    orig_product=None,
    existing_product_variation_updates=None,
    color=None,
    gender=None,
    material=None,
    pattern=None,
    size=None,
):
    ''' create a product or a product variant

    params:
    catalog: catalog this product will belong to
    google_product_category: code for google product category,
    google_product_category_string: string representation of google product category,
    title: Product title,
    description: product description,
    amount: numerical price of product (str),
    inventory: amount of inventory available for product,
    link: product url,
    image_link: product image url,
    brand: brand of product,
    id: product id can be specified but is optional,
    product_group: optional. group for product variant to go into.
    product_group_name: optional.  name for a new product group for variant to go into.
    store: optional but needed for variants, to check if product_group_name already exists.
    orig_product: optional. used if new variant is based on an existing product.
    existing_product_variation_updates: optional. map of variation updates for an existing product.
    color: optional variation field. one of core FB variation fields.
    gender: optional variation field. one of core FB variation fields.
    material: optional variation field. one of core FB variation fields.
    pattern: optional variation field. one of core FB variation fields.
    size: optional variation field. one of core FB variation fields.
    '''
    # create a basic new Product instance
    product = Product(
        title=title,
        description=description,
        amount=amount,
        brand=brand,
        inventory=inventory,
        link=link,
        image_link=image_link,
        google_product_category=google_product_category,
        google_product_category_string=google_product_category_string,
    )
    # apply optional product fields if provided
    if color:
        product.color=color,
    if gender:
        product.gender=gender,
    if material:
        product.material=material,
    if pattern:
        product.pattern=pattern,
    if size:
        product.size=size,
    if id:
        product.id = id

    if orig_product:
        # if an orig_product is provided we are working with a variant
        if existing_product_variation_updates:
            # make product variantion updates according to provided variation updates
            for existing_product_id, updates in existing_product_variation_updates.items():
                existing_product = Product.objects.filter(id=existing_product_id).first()
                for field, val in updates.items():
                    setattr(existing_product, field, val)
                existing_product.save()
        # have to refresh orig_product in case it was updated
        orig_product.refresh_from_db()
        # check that both the orig and new product have variations, and the same variation fields
        if not orig_product.has_variation_info() or not product.has_variation_info():
            raise Exception("You must populate at least one of 'color', 'gender', 'material', 'pattern', 'size' in BOTH products if you wish to create a variant.")
        missing_variations = orig_product._missing_variation_info(product)
        if missing_variations:
            raise Exception("Missing variation info: {}".format(missing_variations))

    if product.has_variation_info():
        # if we are working with a variant
        if not product_group:
            # determine the product_group we are working with
            if product_group_name:
                product_group = ProductGroup.objects.filter(name=product_group_name, store=store).first()
                if not product_group:
                    # if name is provided and does not exist, create the product_group
                    product_group = ProductGroup(name=product_group_name, store=store)
                    product_group.save()
            elif orig_product and orig_product.product_group:
                # if orig_product is provided and it has a product_group, use that one
                product_group = orig_product.product_group
            else:
                # cannot proceed w/o product group.
                raise Exception("You must provide an existing product group or a new product group name if you want to use variation fields such as 'color'")

        # check that all products in product group now has the same variation fields as the new product
        if ProductGroup._missing_variation_info(product_group, product):
            raise Exception("You must provide all existing variants with a value for any new variant fields you are adding to the new product.")

        # check that no product in the product group has EXACTLY the same varition field values as the new product
        if any(product._variation_eq(old_prod) for old_prod in Product.objects.filter(product_group=product_group)):
            raise Exception("A variant with the same variations already exist.")

        # set the new product to the product_group
        product.product_group = product_group
        product.save()
        if orig_product:
            if not orig_product.product_group:
                # if orig_product did not have a product_group, set it to that product_group
                orig_product.product_group = product_group
                orig_product.save()
                # also remove orig_product from the catalog, as now it will be in the catalog only via
                # the product_group
                CatalogItem.objects.filter(product=orig_product).first().delete()
                # add the product_group to the catalog
                cat_item_group = CatalogItemGroup(catalog=catalog,product_group=product_group)
                cat_item_group.save()
        else:
            # if this is a fresh variant not based on an orig_product, just add the product_group to the catalog
            cat_item_group = CatalogItemGroup(catalog=catalog,product_group=product_group)
            cat_item_group.save()
    elif product_group or product_group_name or orig_product:
        # if we are to work with variants, there must be variation info provided
        raise Exception("You must populate at least one of 'color', 'gender', 'material', 'pattern', 'size' if you wish to create a variant.")
    else:
        # we are working with a unique product, not a variant.  just create the product and add it to the catalog.
        product.save()
        cat_item=CatalogItem(catalog=catalog,product=product)
        cat_item.save()

    print("Created product id:{}, title:{}".format(product.id, product.title))
    # only generate proper product url if that's enabled in settings
    # since we do not want to do so in dev since localhost/ type urls are not valid and won't sync to FB
    if settings.GENERATE_PRODUCT_LINK:
        # generate the proper product url.
        product.link = settings.DOMAIN + reverse(
            "viewProduct", args=[catalog.store.id, product.id]
        )
        product.save()

    return product


@transaction.atomic
def update_product(
    product_id: str,
    title: str,
    description: str,
    amount: str,
    inventory: int,
    link: str,
    image_link: str,
    brand="custom",
):
    ''' Update product

    params:
    product_id: product_id of product to update
    title: title of product
    description: description of product
    amoutn: numberial price of product
    invenotry: stock of product available
    link: product url
    image_link: product image url
    bran: product brand
    '''
    product = Product.objects.get(id=product_id)
    product.title = title
    product.description = description
    product.amount = amount
    product.brand = brand
    product.inventory = inventory
    product.link = link
    product.image_link = image_link
    product.save()
    print("product.id (udpated): {}, {}".format(product.id, product.title))
    return product


def post_item_batch_by_id(store_id, allow_upsert=True, items=None):
    store = Store.objects.get(id=store_id)
    return post_item_batch(store, allow_upsert, items)


def post_item_batch(store: Store, allow_upsert=True, items=None):
    ''' sync catalog with FB via POST to batch api's item_batch endpoint

    params:
    store: store whose catalog is to be synced
    items: if provided, only sync these specific items
    '''
    fb_meta = FacebookMetadata.objects.filter(store=store).first()
    if fb_meta is None:
        print(
            "store [{}] doesnot have metadata, aborting catalog sync".format(store.name)
        )
        return
    token = fb_meta.token_info
    if token is None:
        print(
            "store [{}] doesnot have token info, aborting catalog sync".format(
                store.name
            )
        )
        return

    # get the batches of requests
    item_batch_requests = get_catalog_item_batch_requests(store, items)
    data = {
        "access_token": token,
        "item_type": "PRODUCT_ITEM",
        "allow_upsert": allow_upsert,
        "requests": json.dumps(item_batch_requests),
    }
    url = "{}{}/{}/items_batch".format(settings.BASE_API_URL, settings.API_VERSION, str(fb_meta.fb_catalog_id))
    res = requests.post(url, data=data)
    return res


def get_catalog_item_batch_requests(store, items=None):
    """ fetch the catalog and format as catalog item batch api requests

    params:
    store: store to fetch item_batch_requests from
    items: specific items to fetch item_batch_requests from
    """
    if items is None:
        products = [cat_item.product for cat_item in CatalogItem.objects.filter(catalog=store.catalog_id)]
        products += [
            product
            for cig in CatalogItemGroup.objects.filter(catalog=store.catalog_id)
            for product in Product.objects.filter(product_group=cig.product_group)
        ]
        items_requests = [
            {"method": "UPDATE", "data": product.get_json()} for product in products
        ]
    else:
        products = Product.objects.filter(id__in=items)
        items_requests = [
            {"method": "UPDATE", "data": product.get_json()} for product in products
        ]
    return items_requests
