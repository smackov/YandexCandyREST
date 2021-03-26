"""
The administration interface.
"""

from django.contrib import admin

from .models import Courier, WorkingHours, Region

admin.site.register(Courier)
admin.site.register(Region)
admin.site.register(WorkingHours)
