"""
URL Configuration.
"""

from django.urls import path

from . import api


urlpatterns = [
    path('couriers', api.CourierListAPI.as_view(), name='couriers'),
    path('couriers/<int:pk>', api.CourierItemAPI.as_view(), name='courier-item'),
    path('orders', api.OrderListAPI.as_view(), name='orders'),
    path('orders/assign', api.OrdersAssignAPI.as_view(), name='orders-assign'),
    path('orders/complete', api.OrdersCompleteAPI.as_view(), name='orders-complete')
]
