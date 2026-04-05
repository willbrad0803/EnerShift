from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView

handler404 = 'django.views.defaults.page_not_found'
handler500 = 'django.views.defaults.server_error'

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Public marketing pages
    path('', TemplateView.as_view(template_name='public/index.html'), name='home'),
    path('pricing.html', TemplateView.as_view(template_name='public/pricing.html'), name='pricing'),
    path('about.html', TemplateView.as_view(template_name='public/about.html'), name='about'),
    path('demo.html', TemplateView.as_view(template_name='public/demo.html'), name='demo'),
    path('contact.html', TemplateView.as_view(template_name='public/contact.html'), name='contact'),
    path('privacy.html', TemplateView.as_view(template_name='public/privacy.html'), name='privacy'),

    # Dashboard
    path('dashboard/', include('dashboard.urls')),
    
    # Logout
    path('dashboard/logout/', LogoutView.as_view(next_page='home'), name='logout'),
]