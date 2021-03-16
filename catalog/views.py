# Copyright 2004-present, Facebook. All Rights Reserved.
from django.shortcuts import render, redirect

from shop.models import Store
from shop.utils import canViewThisStore
from fb_metadata.utils import getFBEOnboardingDetails
from .models import CatalogItem, CatalogItemGroup, Product
from .forms import CreateProductForm, UpdateProductForm
from .utils import (
    create_product,
    create_dummy_products,
    update_product,
)
from .tasks import sync_catalog_async


def viewProducts(request, storeId):
    ''' view for all products list view of a store '''
    if canViewThisStore(storeId, request.user.id):
        store = Store.objects.get(id=storeId)
        products = [
            i.product for i in CatalogItem.objects.filter(catalog=store.catalog_id)
        ]
        product_groups = [cig.product_group for cig in CatalogItemGroup.objects.filter(catalog=store.catalog_id)]
        # just one variant of each product group
        products += [Product.objects.filter(product_group=product_group).order_by("created").first() for product_group in product_groups]
        metadata = getFBEOnboardingDetails(store.id)
        context = {
            "store": store,
            "fb_metadata": metadata,
            "products": products,
        }
        return render(request, "catalog/products.html", context)

    else:
        return render(request, "403.html")


# view for viewing individual product
def viewProduct(request, storeId, productId):
    ''' view for an individual product detail view '''
    if canViewThisStore(storeId, request.user.id):
        store = Store.objects.get(id=storeId)
        product = Product.objects.get(id=productId)
        metadata = getFBEOnboardingDetails(store.id)
        context = {
            "store": store,
            "fb_metadata": metadata,
            "product": product,
        }
        if product.product_group:
            product_variants = [product for product in Product.objects.filter(product_group=product.product_group).order_by("created") if product.id != productId]
            context["product_variants"] = product_variants

        return render(request, "catalog/product.html", context)
    else:
        return render(request, "403.html")


# view for creating a product for a store
def createProduct(request, storeId):
    ''' view method for creating a product for a store'''
    if canViewThisStore(storeId, request.user.id):
        # get the corresponding store
        store = Store.objects.get(id=storeId)

        if request.method == "POST":
            # Create a form instance and populate it with data from the request (binding):
            form = CreateProductForm(request.POST)

            # Check if the form is valid:
            if form.is_valid():
                # do the create product, then redirect to product view
                product_category_id = request.POST.get("google-product-category-id")
                product_category_string = request.POST.get(
                    "google-product-category-string"
                )
                create_product(
                    store.catalog_id,
                    product_category_id,
                    product_category_string,
                    **form.cleaned_data
                )
                return redirect("viewProducts", storeId)

        form = CreateProductForm(initial={"business_name": store.name})

        breadcrumbs = [
            (store.name, "viewStore", store.id),
            ("Products", "viewProducts", store.id),
        ]
        context = {
            "form": form,
            "page_title": "Create Product",
            "store": store,
            "breadcrumbs": breadcrumbs,
            "needsProductCategories": True,
        }

        return render(request, "core/create.html", context)
    else:
        return render(request, "403.html")


# view for updating a product for a store
def updateProduct(request, productId, storeId):
    ''' view method for updating a specific product for a store '''
    # get the store
    store = Store.objects.get(id=storeId)

    if request.method == "POST":
        form = UpdateProductForm(request.POST)
        # Check if the form is valid:
        if form.is_valid():
            # do the create product, then redirect to product view
            if form.cleaned_data:
                product = update_product(productId, **form.cleaned_data)
                sync_catalog_async.delay(storeId, items=[productId])
            return redirect("viewProducts", storeId)

    product = Product.objects.filter(id=productId).values()[0]
    form = UpdateProductForm(initial={**product})

    breadcrumbs = [
        (store.name, "viewStore", store.id),
        ("Products", "viewProducts", store.id),
    ]
    context = {
        "form": form,
        "page_title": "Update Product",
        "breadcrumbs": breadcrumbs,
        "button": "Update",
    }

    return render(request, "core/update.html", context)


# "view" to call catalog sync function
def syncCatalog(request, storeId):
    ''' view method to call the async task to sync catalog for a store '''
    sync_catalog_async.delay(storeId)
    return redirect("viewProducts", storeId)


def createDummyProducts(request, storeId):
    ''' view method to populate a store's catalog with dummy product and variants '''
    create_dummy_products(storeId)
    return redirect("viewProducts", storeId)
