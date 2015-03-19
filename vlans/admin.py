from django.contrib import admin
from vlans.models import Vlan, Network, IPAddr, Location,Rent
# from vlans.forms import LocationForm

# class LocationAdmin(admin.ModelAdmin):
#     form = LocationForm

# admin.site.register(Node, LocationAdmin)
admin.site.register(Vlan)
admin.site.register(IPAddr)
admin.site.register(Network)
admin.site.register(Location)
admin.site.register(Rent)