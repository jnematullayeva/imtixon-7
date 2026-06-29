from django.contrib import admin

from .models import Appointment, MasterDayOff, MasterProfile, Service, ServiceCategory

admin.site.register(ServiceCategory)
admin.site.register(Service)
admin.site.register(MasterProfile)
admin.site.register(MasterDayOff)
admin.site.register(Appointment)
