# Copyright 2004-present, Facebook. All Rights Reserved.
from django import forms
from .models.carrier_code_choices import CarrierCode


class FulfillOrderForm(forms.Form):
    carrier = forms.ChoiceField(
        label="Carrier Code",
        choices=CarrierCode.choices, initial=CarrierCode.USPS, required = True,
        widget=forms.Select(attrs={"class": "form-control btn btn-secondary dropdown-toggle"}),
    )
    tracking_number = forms.CharField(
        label="Tracking Number",
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "mx-4 p-2 border rounded border-gray-300 text-gray-400"}
        ),
    )
