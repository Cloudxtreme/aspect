from django.contrib import admin
from notes.forms import NoteModelForm
from notes.models import Note

class Note_Admin( admin.ModelAdmin ):
    form = NoteModelForm

admin.site.register(Note, Note_Admin)
