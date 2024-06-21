from django.urls import path
from . import views

urlpatterns = [
    path('', views.fetch_traffic_data, name='fetch_traffic_data'),
]