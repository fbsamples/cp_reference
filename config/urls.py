# Copyright 2004-present, Facebook. All Rights Reserved.
"""cp_reference URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
import os
from django.conf.urls import (
    handler400, handler403, handler404, handler500
)
from webhook import views as webhook_view

handler400 = 'core.views.handler400'
handler403 = 'core.views.handler403'
handler404 = 'core.views.handler404'
handler500 = 'core.views.handler500'

urlpatterns = [
    path(str(os.getenv('DJANGO_SECRET_ADMIN_URL')) + '/admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    # required for facebook webhooks endpoint
    path("webhooks", webhook_view.webhooks, name="webhooks"),
    path("store/<int:storeId>/webhooks",  include("webhook.urls")),
    path("", include("core.urls")),

]
