from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Allauth URLs (handles login, register, password reset, email verification, etc.)
    path('accounts/', include('allauth.account.urls')),
    
    # Dashboard
    path('dashboard/', include('dashboard.urls')),
    
    # Public marketing pages will be added later
    path('', include('dashboard.urls')),  # Temporary - we'll clean this
]
