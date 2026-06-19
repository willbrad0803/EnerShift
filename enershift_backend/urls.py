# enershift_backend/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.account.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('', TemplateView.as_view(template_name='public/index.html'), name='home'),  # Real homepage
]
