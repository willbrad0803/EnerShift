from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView

handler404 = 'django.views.defaults.page_not_found'
handler500 = 'django.views.defaults.server_error'

urlpatterns = [
    path('admin/', admin.site.urls),

    # Dashboard URLs - MUST come BEFORE the public TemplateViews
    path('dashboard/', include('dashboard.urls')),

    # Public marketing pages
    path('', TemplateView.as_view(template_name='public/index.html'), name='home'),
    path('about.html', TemplateView.as_view(template_name='public/about.html')),
    path('demo.html', TemplateView.as_view(template_name='public/demo.html')),
    path('pricing.html', TemplateView.as_view(template_name='public/pricing.html')),
    path('contact.html', TemplateView.as_view(template_name='public/contact.html')),

    # Logout
    path('dashboard/logout/', LogoutView.as_view(next_page='home'), name='logout'),
]
