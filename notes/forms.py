from django import forms
from notes.models import Note

class NoteModelForm( forms.ModelForm ):
    descr = forms.CharField( widget=forms.Textarea )
    class Meta:
        model = Note
