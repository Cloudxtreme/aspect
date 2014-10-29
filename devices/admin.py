from django.contrib import admin
from devices.models import DevType, Device, DeviceStatusEntry, Config, Application

admin.site.register(Device)
admin.site.register(DevType)
admin.site.register(DeviceStatusEntry)
admin.site.register(Config)
admin.site.register(Application)