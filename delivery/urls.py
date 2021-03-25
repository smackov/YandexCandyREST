"""
URL Configuration.
"""

from django.urls import path

from . import api


urlpatterns = [
    path('couriers', api.CourierListAPI.as_view(), name='couriers'),
]
