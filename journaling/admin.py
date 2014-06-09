from django.contrib import admin
from journaling.models import ServiceStatusChanges, AbonentStatusChanges, DeviceStatusEntry
# Register your models here.

admin.site.register(AbonentStatusChanges)
admin.site.register(ServiceStatusChanges)
admin.site.register(DeviceStatusEntry)
