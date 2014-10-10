from django.contrib import admin
# from django.db import models
from notice.models import EmailMessage,TemplateMessage,AbonentEvent

admin.site.register(EmailMessage)
admin.site.register(TemplateMessage)
admin.site.register(AbonentEvent)