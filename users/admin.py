from django.contrib import admin
from users.models import TypeOfService, Plan, Service, Segment, Abonent, Contact, Agent, Bank, Detail, Passport

class ServiceInline(admin.TabularInline):
    model = Service
    extra = 0
    # def get_extra(self, request, obj=None, **kwargs):
    #     extra = 2
    #     if obj:
    #         return extra - obj.service_set.count()
    #     return extra

class DetailInline(admin.TabularInline):
    model = Detail
    extra = 0

class PassportInline(admin.TabularInline):
    model = Passport
    extra = 0

class AbonentAdmin(admin.ModelAdmin):
    inlines = [
        ServiceInline,
        PassportInline,
        DetailInline,
    ]

admin.site.register(TypeOfService)
admin.site.register(Plan)
admin.site.register(Agent)
# admin.site.register(Service)
admin.site.register(Segment)
admin.site.register(Abonent, AbonentAdmin)
admin.site.register(Contact)
admin.site.register(Bank)