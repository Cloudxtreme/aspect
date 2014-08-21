from django.contrib import admin
from users.models import TypeOfService, Plan, Service, Segment, Abonent, Agent, Bank, Detail, Passport, ServiceSuspension
# from django.contrib.admin.models import LogEntry

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

class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'action_time', 'user', 'content_type', 'object_id', 'object_repr', 'action_flag', 'change_message')
    list_filter = ('content_type',)
    search_fields = ['user__username',]
    date_hierarchy = 'action_time'

# admin.site.register(LogEntry, LogEntryAdmin)

admin.site.register(TypeOfService)
admin.site.register(Plan)
admin.site.register(Agent)
# admin.site.register(Service)
admin.site.register(Segment)
admin.site.register(Abonent, AbonentAdmin)
# admin.site.register(Contact)
admin.site.register(Bank)
admin.site.register(ServiceSuspension)