from django.contrib import admin
from devices.models import DevType, Device, DeviceStatusEntry, Config

admin.site.register(Device)
admin.site.register(DevType)
admin.site.register(DeviceStatusEntry)
admin.site.register(Config)