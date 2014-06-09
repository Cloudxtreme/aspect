from django.contrib import admin
from django.forms import Textarea
from django.db import models
from tt.models import TroubleTicketCategory, TroubleTicket, TroubleTicketComment

# Register your models here.

class TroubleTicketCommentInline(admin.TabularInline):
    model = TroubleTicketComment
    formfield_overrides = {
        models.CharField: {'widget': Textarea},
    }

class TroubleTicketAdmin(admin.ModelAdmin):
    inlines = [
        TroubleTicketCommentInline,
    ]
    # formfield_overrides = {
    #     models.CharField: {'widget': Textarea},
    # }

admin.site.register(TroubleTicket, TroubleTicketAdmin)
admin.site.register(TroubleTicketCategory)