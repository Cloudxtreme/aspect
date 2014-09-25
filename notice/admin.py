from django.contrib import admin
# from django.db import models
from notice.models import EmailMessage,GroupEmailMessage

admin.site.register(EmailMessage)
admin.site.register(GroupEmailMessage)