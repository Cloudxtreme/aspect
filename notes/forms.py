from django import forms
from notes.models import Note

# class AdminNoteModelForm(forms.ModelForm):
    
#     class Meta:
#         model = Note
#         widgets = {
#             'descr': forms.Textarea(),
#         }

class NoteModelForm(forms.ModelForm):
    
    class Meta:
        model = Note
        exclude = ['author','read','kind']
        widgets = {
            # 'descr': forms.Textarea(),
        }
    
    def __init__(self, *args, **kwargs):
        super(NoteModelForm, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
