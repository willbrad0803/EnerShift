from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Allauth Authentication (Primary)
    path('accounts/', include('allauth.account.urls')),
    
    # Dashboard
    path('dashboard/', include('dashboard.urls')),
    
    # Root URL - Redirect to Allauth Login
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False), name='home'),
]
