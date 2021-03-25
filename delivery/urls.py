"""
URL Configuration.
"""

from django.urls import path

from . import api


urlpatterns = [
    path('couriers', api.CouriersListAPI.as_view(), name='couriers'),
]
