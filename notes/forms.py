from django import forms
from notes.models import Note

class NoteModelForm( forms.ModelForm ):
    descr = forms.CharField( widget=forms.Textarea )
    class Meta:
        model = Note
    
    def __init__(self, *args, **kwargs):
        super(NoteModelForm, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
