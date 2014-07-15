from django.contrib import admin
# from contacts.forms import ContactModelForm
from contacts.models import Contact

# class Note_Admin( admin.ModelAdmin ):
#     form = NoteModelForm

admin.site.register(Contact)