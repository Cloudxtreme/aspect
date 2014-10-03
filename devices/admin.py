from django.contrib import admin
from devices.models import DevType, Device, Iface, DeviceStatusEntry

class IfaceInline(admin.TabularInline):
    model = Iface
    extra = 0

class DeviceAdmin(admin.ModelAdmin):
    inlines = [
        IfaceInline,
    ]

admin.site.register(Device,DeviceAdmin)
admin.site.register(Iface)
admin.site.register(DevType)
admin.site.register(DeviceStatusEntry)
