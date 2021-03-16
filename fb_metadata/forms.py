# Copyright 2004-present, Facebook. All Rights Reserved.
from django import forms

class FbeOnboardingForm(forms.Form):
    business_name = forms.CharField(
        label="Business Name",
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control py-4"}),
        disabled=True,
    )
