from django.contrib import admin
from devices.models import DevType, Device

admin.site.register(Device)
admin.site.register(DevType)