from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('overview/', views.all_sites_overview, name='all_sites_overview'),
    path('add-site/', views.add_site, name='add_site'),
    path('site/<int:site_id>/', views.site_detail, name='site_detail'),
    path('delete/<int:site_id>/', views.delete_site, name='delete_site'),
    path('upload-consumption/<int:site_id>/', views.upload_consumption, name='upload_consumption'),
    
    # Auth
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register, name='register'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),   # ← Must match email
]
