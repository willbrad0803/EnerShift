from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('register/', views.register, name='register'),        # New register route
    path('', views.dashboard_home, name='dashboard_home'),
    path('overview/', views.all_sites_overview, name='all_sites_overview'),
    path('add-site/', views.add_site, name='add_site'),
    path('site/<int:site_id>/', views.site_detail, name='site_detail'),
    path('site/<int:site_id>/delete/', views.delete_site, name='delete_site'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
]
