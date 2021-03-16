# Copyright 2004-present, Facebook. All Rights Reserved.
import os

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

from .forms import UserRegistrationForm


def register(request):
    """ this view lets a user register on the site """
    is_registration_allowed = os.getenv("ALLOW_USER_REGISTRATIONS", 0)
    print(is_registration_allowed)
    if is_registration_allowed != "TRUE":
        return render(request, "403.html")

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect("index")
    else:
        form = UserRegistrationForm()

    context = {"form": form}
    return render(request, "registration/register.html", context)
