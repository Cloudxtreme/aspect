from django import forms
from django.contrib.auth.models import User
from tt.models import TroubleTicket

class TTForm( forms.ModelForm ):
    def __init__(self, *args, **kwargs):
        super(TTForm, self).__init__(*args, **kwargs)
        users = User.objects.all()
        self.fields['performer'].choices = [(user.pk, user.get_full_name()) for user in users]

    class Meta:
        model = TroubleTicket
        fields = ['number', 'performer', 'category', 'description']
        widgets = {
            'number': forms.TextInput(attrs={'class': 'form-control',}),
            'performer': forms.Select(attrs={'class': 'form-control', }),
            'category': forms.Select(attrs={'class': 'form-control', }),
            'description': forms.Textarea(attrs={'class': 'form-control','rows': 10, 'cols': 20}),
        }
