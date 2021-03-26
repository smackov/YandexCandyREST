"""
URL Configuration.
"""

from django.urls import path

from . import api


urlpatterns = [
    path('couriers', api.CourierListAPI.as_view(), name='couriers'),
    path('couriers/<int:pk>', api.CourierItemAPI.as_view(), name='courier-item'),
]
