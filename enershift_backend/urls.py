from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.account.urls')),  # This must be first for allauth patterns
    path('dashboard/', include('dashboard.urls')),
    path('', TemplateView.as_view(template_name='public/index.html'), name='home'),
    path('about/', TemplateView.as_view(template_name='public/about.html'), name='about'),
    path('pricing/', TemplateView.as_view(template_name='public/pricing.html'), name='pricing'),
    path('contact/', TemplateView.as_view(template_name='public/contact.html'), name='contact'),
    path('demo/', TemplateView.as_view(template_name='public/demo.html'), name='demo'),
]
