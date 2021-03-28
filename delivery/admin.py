"""
The administration interface.
"""

from django.contrib import admin

from .models import (
    Courier, WorkingHours, Region, DeliveryHours, Order, AssignedOrderSet)

admin.site.register(Courier)
admin.site.register(Region)
admin.site.register(WorkingHours)
admin.site.register(Order)
admin.site.register(DeliveryHours)
admin.site.register(AssignedOrderSet)
