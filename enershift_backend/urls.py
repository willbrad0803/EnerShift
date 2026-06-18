from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Allauth
    path('accounts/', include('allauth.account.urls')),
    
    # Dashboard
    path('dashboard/', include('dashboard.urls')),
    
    # Public Marketing Home (original static style)
    path('', TemplateView.as_view(template_name='public/index.html'), name='home'),
    
    # Other public pages if needed
    path('about/', TemplateView.as_view(template_name='public/about.html'), name='about'),
]
