from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('overview/', views.all_sites_overview, name='all_sites_overview'),
    path('add-site/', views.add_site, name='add_site'),
    path('site/<int:site_id>/', views.site_detail, name='site_detail'),
    path('site/<int:site_id>/delete/', views.delete_site, name='delete_site'),
]