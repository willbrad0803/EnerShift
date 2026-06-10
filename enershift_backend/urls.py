from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Allauth Authentication
    path('accounts/', include('allauth.account.urls')),
    
    # Dashboard
    path('dashboard/', include('dashboard.urls')),
    
    # Root -> Login
    path('', lambda request: redirect('account_login'), name='home'),
]
