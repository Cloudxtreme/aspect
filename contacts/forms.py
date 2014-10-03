from django import forms
from contacts.models import Contact

class ContactModelForm( forms.ModelForm ):
    # descr = forms.CharField( widget=forms.Textarea )
    class Meta:
        model = Contact
        exclude = ['abonent']
    
    def __init__(self, *args, **kwargs):
        super(ContactModelForm, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
