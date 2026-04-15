from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Dashboard must come BEFORE the public pages
    path('dashboard/', include('dashboard.urls')),

    # Public pages
    path('', TemplateView.as_view(template_name='public/index.html'), name='home'),
    path('about.html', TemplateView.as_view(template_name='public/about.html')),
    path('demo.html', TemplateView.as_view(template_name='public/demo.html')),
    path('pricing.html', TemplateView.as_view(template_name='public/pricing.html')),
    path('contact.html', TemplateView.as_view(template_name='public/contact.html')),
]
