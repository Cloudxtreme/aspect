from django.contrib import admin
from pays.models import PaymentSystem, Payment, WriteOffType, WriteOff, PromisedPays

# class WriteOffAdmin(admin.ModelAdmin):
#     form = WriteOffForm

admin.site.register(PromisedPays)
admin.site.register(PaymentSystem)
admin.site.register(Payment)
admin.site.register(WriteOffType)
admin.site.register(WriteOff)