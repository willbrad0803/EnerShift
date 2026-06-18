from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.account.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('', lambda request: redirect('account_login'), name='home'),
]
