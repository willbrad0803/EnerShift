from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard_home, name='dashboard_home'),
    path('add-site/', views.add_site, name='add_site'),
    path('site/<int:site_id>/', views.site_detail, name='site_detail'),
    path('delete/<int:site_id>/', views.delete_site, name='delete_site'),

    # Auth
   path('login/', auth_views.LoginView.as_view(
    template_name='registration/login.html',
    redirect_authenticated_user=True   # Important
), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
]



