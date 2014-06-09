from django.contrib import admin
from vlans.models import Vlan, DevType, Device, Node, Network, IPAddr
from vlans.forms import LocationForm

class LocationAdmin(admin.ModelAdmin):
    form = LocationForm

admin.site.register(Node, LocationAdmin)
admin.site.register(Vlan)
admin.site.register(IPAddr)
admin.site.register(Device)
admin.site.register(DevType)
admin.site.register(Network)