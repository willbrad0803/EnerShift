from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('add-site/', views.add_site, name='add_site'),
    path('logout/', views.custom_logout, name='logout'),
]
