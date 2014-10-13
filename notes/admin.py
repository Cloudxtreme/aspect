from django.contrib import admin
# from notes.forms import AdminNoteModelForm
from notes.models import Note

# class Note_Admin( admin.ModelAdmin ):
#     form = AdminNoteModelForm

admin.site.register(Note)
# admin.site.register(Note,Note_Admin)
