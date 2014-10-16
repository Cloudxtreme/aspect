from django.contrib import admin
from devices.models import DevType, Device, SubInterface, DeviceStatusEntry

class SubInterfaceInline(admin.TabularInline):
    model = SubInterface
    extra = 0

class DeviceAdmin(admin.ModelAdmin):
    inlines = [
        SubInterfaceInline,
    ]

admin.site.register(Device,DeviceAdmin)
admin.site.register(SubInterface)
admin.site.register(DevType)
admin.site.register(DeviceStatusEntry)
