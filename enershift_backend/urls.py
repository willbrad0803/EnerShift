from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Allauth (this is the main auth system)
    path('accounts/', include('allauth.account.urls')),
    
    # Dashboard
    path('dashboard/', include('dashboard.urls')),
    
    # Temporary root redirect to login for now
    path('', lambda r: redirect('account_login'), name='home'),
]
