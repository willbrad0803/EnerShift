from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    # Login page - this is the key fix
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),

    # Main dashboard (protected)
    path('', views.dashboard_home, name='dashboard_home'),

    # Other dashboard routes
    path('overview/', views.all_sites_overview, name='all_sites_overview'),
    path('add-site/', views.add_site, name='add_site'),
    path('site/<int:site_id>/', views.site_detail, name='site_detail'),
    path('site/<int:site_id>/delete/', views.delete_site, name='delete_site'),

    # Logout
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
]
