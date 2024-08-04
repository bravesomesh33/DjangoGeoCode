from django.urls import path
from .views import CalculateDistanceView

urlpatterns = [
    path('calculate/', CalculateDistanceView.as_view(), name='calculate_distance'),
]
