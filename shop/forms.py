# Copyright 2004-present, Facebook. All Rights Reserved.
from django import forms

from .models.choices import Currency


class StoreCreationForm(forms.Form):
    """
    This form is used when creating a store.
    """

    _TIMEZONES = ["America/Los_Angeles"]

    business_name = forms.CharField(
        label="Name",
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control py-4"}),
    )

    unique_business_id = forms.CharField(
        label="Unique Business ID",
        max_length=100,
        help_text="This is YOUR unique identifier for this merchant, but many platforms may choose to just generate a numeric ID.",
        widget=forms.TextInput(
            attrs={"class": "form-control py-4", "placeholder": "Optional"}
        ),
        required=False,
    )
    timezone = forms.ChoiceField(
        choices=([(i, i) for i in _TIMEZONES]),
        initial="1",
        required=True,
        widget=forms.Select(
            attrs={"class": "form-control btn btn-secondary dropdown-toggle"}
        ),
    )
    currency = forms.ChoiceField(
        choices=Currency.choices,
        initial=Currency.USD,
        required=True,
        widget=forms.Select(
            attrs={"class": "form-control btn btn-secondary dropdown-toggle"}
        ),
    )


class UpdateStoreForm(forms.Form):
    """
    This form is used when updating a store.
    """

    business_name = forms.CharField(
        label="Business Name",
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "mx-4 p-2 border rounded border-gray-300 text-gray-400"}
        ),
    )
