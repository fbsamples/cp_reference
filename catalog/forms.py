# Copyright 2004-present, Facebook. All Rights Reserved.
from django import forms


class CreateProductForm(forms.Form):
    title = forms.CharField(
        label="Product Title",
        max_length=255,
        widget=forms.TextInput(
            attrs={"class": "mx-4 p-2 border rounded border-gray-300 text-gray-400"}
        ),
    )
    description = forms.CharField(
        label="Description",
        max_length=2048,
        widget=forms.Textarea(
            attrs={"class": "mx-4 p-2 border rounded border-gray-300 text-gray-400", "rows": 5, "cols": 20}
        ),
    )
    amount = forms.DecimalField(
        label="Amount",
        max_value=500000,
        min_value=0,
        decimal_places=2,
        max_digits=8,
        widget=forms.NumberInput(
            attrs={
                "class": "mx-4 p-2 border rounded border-gray-300 text-gray-400",
                "step": "0.01",
            }
        ),
    )
    brand = forms.CharField(
        label="Brand",
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "mx-4 p-2 border rounded border-gray-300 text-gray-400"}
        ),
    )
    inventory = forms.IntegerField(
        label="Inventory",
        widget=forms.NumberInput(
            attrs={"class": "mx-4 p-2 border rounded border-gray-300 text-gray-400"}
        ),
    )
    link = forms.CharField(
        label="Product URL",
        max_length=1024,
        widget=forms.TextInput(
            attrs={"class": "mx-4 p-2 border rounded border-gray-300 text-gray-400"}
        ),
    )
    image_link = forms.CharField(
        label="Product Image URL",
        max_length=1024,
        widget=forms.TextInput(
            attrs={"class": "mx-4 p-2 border rounded border-gray-300 text-gray-400"}
        ),
    )


class UpdateProductForm(forms.Form):
    title = forms.CharField(
        required=False,
        label="Product Title",
        max_length=255,
        widget=forms.TextInput(
            attrs={"class": "mx-4 p-2 border rounded border-gray-300 text-gray-400"}
        ),
    )
    description = forms.CharField(
        required=False,
        label="Description",
        max_length=2048,
        widget=forms.Textarea(
            attrs={"class": "mx-4 p-2 border rounded border-gray-300 text-gray-400", "rows": 5, "cols": 20}
        ),
    )
    amount = forms.DecimalField(
        required=False,
        label="Amount",
        max_value=500000,
        min_value=0,
        decimal_places=2,
        max_digits=8,
        widget=forms.NumberInput(
            attrs={
                "class": "mx-4 p-2 border rounded border-gray-300 text-gray-400",
                "step": "0.01",
            }
        ),
    )
    brand = forms.CharField(
        required=False,
        label="Brand",
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "mx-4 p-2 border rounded border-gray-300 text-gray-400"}
        ),
    )
    inventory = forms.IntegerField(
        required=False,
        label="Inventory",
        widget=forms.NumberInput(
            attrs={"class": "mx-4 p-2 border rounded border-gray-300 text-gray-400"}
        ),
    )
    link = forms.CharField(
        required=False,
        label="Product URL",
        max_length=1024,
        widget=forms.TextInput(
            attrs={"class": "mx-4 p-2 border rounded border-gray-300 text-gray-400"}
        ),
    )
    image_link = forms.CharField(
        required=False,
        label="Product Image URL",
        max_length=1024,
        widget=forms.TextInput(
            attrs={"class": "mx-4 p-2 border rounded border-gray-300 text-gray-400"}
        ),
    )
