# Copyright 2004-present, Facebook. All Rights Reserved.
import uuid

from django.db import models
from typing import List, Dict

from core.models import BaseModel
from core.models.utils import datetime_utc_now_with_tz
from shop.models import Store
from shop.models.choices import Currency
from .catalog import Catalog
from .choices import Availability, Condition, Visibility
from .collections import Collection

class ProductSet(BaseModel):
    """Represents a single Product Set.
    A Product Set is a logical compilation of products, related by some criteria,
    eg "fall collection", "electronics", "gifts < $10" etc.

    fields:
    collection: the collection  this Product Set belongs to
    """

    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, blank=True, null=True)
    catalog = models.ForeignKey(Catalog, on_delete=models.CASCADE)


class ProductGroup(BaseModel):
    """Represents a Product Group.
    A Product Group is a group of VARIANTS of a SINGLE item.

    For example, a specific design of t shirt with 3 base shirt colors,
    3 sizes, and 2 cuts could be 18 unique preducts, but is still "the same shirt".
    Thus said shirt design would have a product group, and it will contain all the
    products representing combinations of variations of that item.

    """
    # name: name of the product group
    name = models.CharField(
            max_length=100, default=uuid.uuid4
    )
    # product_set: the product set this product group belongs to
    product_set = models.ForeignKey(ProductSet, on_delete=models.CASCADE, blank=True, null=True)
    # store: the store this product group belongs to
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    # core FB variation fields to be used for managing variant information of items in the group
    color = models.BooleanField(default=False)
    color_variants = models.TextField(blank=True, null=True)
    gender = models.BooleanField(default=False)
    gender_variants = models.TextField(blank=True, null=True)
    material = models.BooleanField(default=False)
    material_variants = models.TextField(blank=True, null=True)
    pattern = models.BooleanField(default=False)
    pattern_variants = models.TextField(blank=True, null=True)
    size = models.BooleanField(default=False)
    size_variants = models.TextField(blank=True, null=True)
    # custom variations.  should be comma separated key:value pairs.
    # ex: Scent:Fruity,Hypoallergenic:Yes,
    additional_variations = models.TextField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['store', 'name'], name='unique_product_group_name_for_store')
        ]

    @staticmethod
    def _missing_variation_info(product_group, new_product):
        ''' helper method to determine if any products in group have none-matching variation fields compared to new_product '''
        existing_products = Product.objects.filter(product_group=product_group)
        return any(new_product._missing_variation_info(product) for product in existing_products)


class Product(BaseModel):
    """Represents a unique Product.
    A Product is a direct representation of a unique and specific product VARIANT.
    Products can exist without variations.

    """

    id = models.CharField(
        max_length=100, blank=True, unique=True, default=uuid.uuid4, primary_key=True
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    # formatted description
    rich_text_description = models.TextField(blank=True, default="")
    # availability state of the product.  private so that we can use "availability"
    # as a class property name, to make getting product info for syncing easier
    _availability = models.CharField(
        max_length=12,
        choices=Availability.choices,
        default=Availability.IN_STOCK,
    )
    # date product was created on local db
    created = models.DateTimeField(default=datetime_utc_now_with_tz, blank=True)

    # human readable, and FB batch api compatible availability state
    @property
    def availability(self):
        return self.get__availability_display()
    # product stock available
    inventory = models.IntegerField()
    # product condition
    condition = models.CharField(
        max_length=6,
        choices=Condition.choices,
        default=Condition.NEW,
    )
    # numerical price of product
    amount = models.DecimalField(decimal_places=2, max_digits=7)
    # currency of product
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.USD,
    )

    # human readable and FB batch api compatible product price
    @property
    def price(self):
        return " ".join([str(self.amount), self.currency])

    # product url
    link = models.TextField()
    # product image url
    image_link = models.TextField()
    # product brand
    brand = models.CharField(max_length=255)
    # secondary image url
    additional_image_link = models.TextField(blank=True, default="")
    # Age group for the product. optional but FB natively support product info field
    age_group = models.CharField(max_length=255, blank=True, default="")
    # Product Color. FB core variantion field.  do not use as a custom variation field.
    color = models.CharField(max_length=255, blank=True, default="")
    # Product gender. FB core variantion field.  do not use as a custom variation field.
    gender = models.CharField(max_length=255, blank=True, default="")
    # if exists, product group this product variant belongs to
    product_group = models.ForeignKey(
        ProductGroup,
        related_name="product_group_type",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    # FB batch api compatible product_group name
    @property
    def item_group_id(self):
        return self.product_group and self.product_group.name

    # string representation of the products google product category
    google_product_category_string = models.CharField(
        max_length=255, blank=True, default=""
    )
    # code for the products google product category
    google_product_category = models.CharField(max_length=255, blank=True, default="")
    # Product material. FB core variantion field.  do not use as a custom variation field.
    material = models.CharField(max_length=255, blank=True, default="")
    # Product pattern. FB core variantion field.  do not use as a custom variation field.
    pattern = models.CharField(max_length=255, blank=True, default="")
    # Product type.  FB natively supported product info field.
    product_type = models.CharField(max_length=255, blank=True, default="")
    # numerical discounted price of product
    sale_price = models.DecimalField(
        decimal_places=2, max_digits=7, null=True, blank=True
    )
    # effective date of sale price
    sale_price_effective_date = models.DateTimeField(null=True, blank=True)
    # shipping cost of the product.
    #   this is SPACE DELIMITED ex: US:CA:Ground:9.99 USD,US:NY:Air:15.99 USD
    #   ex with no region: SG::Air:14.99 SGD
    shipping = models.TextField(blank=True, null=True)
    # Shipping weight of the item in lb, oz, g, or kg.
    # ex: 10 kg
    shipping_weight = models.TextField(blank=True, null=True)
    # size of product
    size = models.CharField(max_length=255, blank=True, default="")
    # product visibility. staging or published.
    visibility = models.CharField(
        max_length=14,
        choices=Visibility.choices,
        default=Visibility.PUBLISHED,
    )
    # product mobile url
    mobile_link = models.TextField(blank=True, null=True)
    # custom variations
    # this is COMMA DELIMITED: Scent:Fruity,Flavor:
    additional_variant_attribute = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

    def get_reqd_headings_list(self):
        # get list of fields for syncing
        headings = [
            "id",
            "title",
            "description",
            "rich_text_description",
            "availability",
            "condition",
            "price",
            "brand",
            "visibility",
            "inventory",
            "link",
            "image_link",
        ]
        # only add to this heading list when it exists
        if self.google_product_category != "":
            headings.append("google_product_category")
        if self.product_group: headings.append("item_group_id")
        if self.color: headings.append("color")
        if self.gender: headings.append("gender")
        if self.material: headings.append("material")
        if self.pattern: headings.append("pattern")
        if self.size: headings.append("size")
        return headings

    def get_json(self):
        # get the json for syncing this product
        data = {h: getattr(self, h) for h in self.get_reqd_headings_list()}
        return data

    def has_variation_info(self):
        # check the product instance has variations
        return self.color or self.gender or self.material or self.pattern or self.size or self.additional_variant_attribute

    def _need_variation_field(self, other, field_name)->List[str]:
        # check one of two products is missing a particular variation field
        if not getattr(self, field_name) and getattr(other, field_name):
            return ["orig"]
        elif getattr(self, field_name) and not getattr(other, field_name):
            return ["new"]
        return []

    def _missing_variation_info(self, other)->Dict:
        # check if two products have different variation fields populated
        result = {}
        field_names = ["color", "gender", "material", "pattern", "size"]
        for field_name in field_names:
            for prod in self._need_variation_field(other, field_name):
                result.setdefault(prod,[]).append(field_name)
        return result

    def _variation_eq(self, other):
        # check two products have identical variation fields and values
        field_names = ["color", "gender", "material", "pattern", "size"]
        self_fields = set()
        eq_fields = set()
        for field_name in field_names:
            field_val = getattr(self, field_name)
            if field_val:
                self_fields.add(field_name)
                if field_val == getattr(other, field_name):
                    eq_fields.add(field_name)
        if eq_fields==self_fields:
            return True



class ProductGroupItem(BaseModel):
    """Represents one unique product that is a variation that belongs in a
    Product Group
    """

    product_group = models.ForeignKey(ProductGroup, on_delete=models.CASCADE)
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        primary_key=True,
    )


class ProductSetItem(BaseModel):
    """Represents one unique product item that is a member of a product set"""

    product_set = models.ForeignKey(ProductSet, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
