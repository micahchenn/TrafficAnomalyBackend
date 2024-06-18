from django.urls import path
from . import views

urlpatterns = [
    path('', views.anomaly_detection_view, name='traffic_handler'),
]