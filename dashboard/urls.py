# dashboard/urls.py (update)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('add-site/', views.add_site, name='add_site'),
    path('upload-meter/', views.upload_meter_data, name='upload_meter_data'),
    path('recommendations/<int:site_id>/', views.get_recommendations, name='get_recommendations'),
    path('logout/', views.custom_logout, name='logout'),
]
